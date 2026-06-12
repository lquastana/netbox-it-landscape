"""
Import des données de l'application it-landscape (fichiers JSON) dans le plugin.

Usage :
    manage.py import_it_landscape /chemin/vers/data [--create-sites]

Le répertoire doit contenir les fichiers du dépôt it-landscape :
    <etablissement>.json        (cartographie métier)
    <etablissement>.flux.json   (flux applicatifs)
    <etablissement>.infra.json  (serveurs, pour le rattachement VM ↔ application)
    trigrammes.json             (référentiel trigramme → nom d'application)
"""
import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from dcim.models import Site
from extras.models import Tag
from ipam.models import IPAddress, Prefix, VLAN
from virtualization.models import VirtualMachine, VMInterface

from netbox_it_landscape.choices import (
    CriticalityChoices,
    DOMAIN_COLOR_PALETTE,
    InterfaceTypeChoices,
)
from netbox_it_landscape.models import (
    Application,
    ApplicationFlow,
    BusinessDomain,
    BusinessProcess,
)

INTERFACE_FIELD_MAP = {
    'Administrative': 'interface_administrative',
    'Medicale': 'interface_medicale',
    'Facturation': 'interface_facturation',
    'Planification': 'interface_planification',
    'Autre': 'interface_autre',
}

INTERFACE_TYPE_MAP = {
    'administrative': InterfaceTypeChoices.ADMINISTRATIVE,
    'medicale': InterfaceTypeChoices.MEDICALE,
    'facturation': InterfaceTypeChoices.FACTURATION,
    'planification': InterfaceTypeChoices.PLANIFICATION,
    'autre': InterfaceTypeChoices.AUTRE,
}

FALLBACK_DOMAIN = 'Hors référentiel métier'
FALLBACK_PROCESS = 'À classer'


class Command(BaseCommand):
    help = "Importe les données it-landscape (JSON) dans les modèles du plugin"

    def add_arguments(self, parser):
        parser.add_argument('data_dir', help='Répertoire contenant les fichiers JSON it-landscape')
        parser.add_argument(
            '--create-sites', action='store_true',
            help="Crée les sites NetBox manquants au lieu de les ignorer",
        )
        parser.add_argument(
            '--with-infra', action='store_true',
            help="Crée aussi l'infrastructure NetBox : VM (IP, interfaces, tags), VLAN, préfixes et passerelles",
        )

    def handle(self, *args, **options):
        data_dir = Path(options['data_dir'])
        if not data_dir.is_dir():
            raise CommandError(f'Répertoire introuvable : {data_dir}')

        self.create_sites = options['create_sites']
        self.with_infra = options['with_infra']
        self.stats = {
            'domains': 0, 'processes': 0, 'applications': 0,
            'flows': 0, 'vm_links': 0, 'skipped_flows': 0,
            'vms': 0, 'vlans': 0, 'prefixes': 0,
        }

        self.trigramme_names = self._load_json(data_dir / 'trigrammes.json') or {}

        metier_files = [
            f for f in sorted(data_dir.glob('*.json'))
            if not f.name.endswith(('.flux.json', '.infra.json', '.network.json'))
            and f.name != 'trigrammes.json'
        ]
        if not metier_files:
            raise CommandError(f'Aucun fichier de cartographie métier trouvé dans {data_dir}')

        for metier_file in metier_files:
            data = self._load_json(metier_file)
            if not data or 'etablissements' not in data:
                continue
            base = metier_file.stem
            infra = self._load_json(data_dir / f'{base}.infra.json')
            network = self._load_json(data_dir / f'{base}.network.json')
            flux = self._load_json(data_dir / f'{base}.flux.json')
            for etab in data['etablissements']:
                self._import_etablissement(etab, infra, network, flux)

        self.stdout.write(self.style.SUCCESS(
            "Import terminé : "
            f"{self.stats['domains']} domaines, "
            f"{self.stats['processes']} processus, "
            f"{self.stats['applications']} applications, "
            f"{self.stats['flows']} flux, "
            f"{self.stats['vm_links']} liens VM"
            + (
                f", {self.stats['vms']} VM, {self.stats['vlans']} VLAN, "
                f"{self.stats['prefixes']} préfixes"
                if self.with_infra else ""
            )
            + (f" ({self.stats['skipped_flows']} flux ignorés)" if self.stats['skipped_flows'] else "")
        ))

    # ──────────────────────────────────────────────────────────────────────

    def _load_json(self, path):
        if not path.exists():
            return None
        with open(path, encoding='utf-8') as fh:
            return json.load(fh)

    def _get_site(self, name):
        site = Site.objects.filter(name__iexact=name).first()
        if site:
            return site
        if self.create_sites:
            site = Site.objects.create(name=name, slug=slugify(name)[:100], status='active')
            self.stdout.write(f'  Site créé : {name}')
            return site
        self.stderr.write(self.style.WARNING(
            f'Site NetBox introuvable pour « {name} » — établissement ignoré '
            '(utilisez --create-sites pour le créer)'
        ))
        return None

    def _import_etablissement(self, etab, infra, network, flux):
        name = (etab.get('nom') or '').strip()
        if not name:
            return
        site = self._get_site(name)
        if not site:
            return

        self.stdout.write(self.style.MIGRATE_HEADING(f'Établissement : {name}'))

        # Infrastructure NetBox (VM, VLAN, préfixes) avant le rattachement
        if self.with_infra:
            if infra:
                self._seed_vms(site, infra)
            if network:
                self._seed_network(site, network)

        # Domaines → processus → applications
        app_index = {}
        for idx, dom in enumerate(etab.get('domaines', [])):
            domain, created = BusinessDomain.objects.update_or_create(
                site=site,
                name=dom.get('nom', '').strip(),
                defaults={
                    'description': (dom.get('description') or '')[:200],
                    'color': DOMAIN_COLOR_PALETTE[idx % len(DOMAIN_COLOR_PALETTE)],
                },
            )
            if created:
                self.stats['domains'] += 1
            for proc in dom.get('processus', []):
                process, created = BusinessProcess.objects.update_or_create(
                    domain=domain,
                    name=proc.get('nom', '').strip(),
                    defaults={'description': (proc.get('description') or '')[:200]},
                )
                if created:
                    self.stats['processes'] += 1
                for app_data in proc.get('applications', []):
                    app = self._import_application(process, app_data)
                    if app and app.trigramme:
                        app_index.setdefault(app.trigramme, app)

        # Rattachement des serveurs (VM NetBox) par trigramme
        if infra:
            self._link_servers(site, infra, app_index)

        # Flux applicatifs
        if flux:
            self._import_flux(site, flux, app_index)

    def _import_application(self, process, data):
        name = (data.get('nom') or '').strip()
        if not name:
            return None

        interfaces = data.get('interfaces') or {}
        defaults = {
            'trigramme': (data.get('trigramme') or '').strip().upper()[:10],
            'description': (data.get('description') or '')[:500],
            'editor': (data.get('editeur') or '')[:100],
            'referent': (data.get('referent') or '')[:100],
            'hosting': (data.get('hebergement') or '')[:100],
            'criticality': (
                CriticalityChoices.CRITICAL
                if (data.get('criticite') or '').lower() == 'critique'
                else CriticalityChoices.STANDARD
            ),
            'multi_site': bool(data.get('multiEtablissement')),
            'monitoring_url': (data.get('lienPRTG') or '')[:200],
        }
        for key, field in INTERFACE_FIELD_MAP.items():
            defaults[field] = bool(interfaces.get(key))

        app, created = Application.objects.update_or_create(
            process=process, name=name, defaults=defaults,
        )
        if created:
            self.stats['applications'] += 1
        return app

    def _seed_vms(self, site, infra):
        """Crée les VM NetBox du fichier *.infra.json (IP primaire, interface, tag app:XXX)."""
        for server in infra.get('serveurs', []):
            vm_name = (server.get('VM') or '').strip()
            if not vm_name:
                continue

            tri = (server.get('trigramme') or '').strip().upper()
            comments = '\n'.join(filter(None, [
                f"OS: {server['OS']}" if server.get('OS') else '',
                f"Backup: {server['Backup']}" if server.get('Backup') else '',
                f"Éditeur: {server['Editeur']}" if server.get('Editeur') else '',
                f"Contact: {server['Contact']}" if server.get('Contact') else '',
            ]))

            vm, created = VirtualMachine.objects.get_or_create(
                name=vm_name, site=site,
                defaults={
                    'status': 'active',
                    'description': (server.get('RoleServeur') or '')[:200],
                    'vcpus': server.get('CPUs') or None,
                    'memory': server.get('MemoryMiB') or None,
                    'disk': round((server.get('TotalDiskCapacityMiB') or 0) / 1024) or None,
                    'comments': comments,
                },
            )
            if created:
                self.stats['vms'] += 1

            if tri:
                tag_name = f'app:{tri}'
                tag, _ = Tag.objects.get_or_create(
                    slug=slugify(tag_name),
                    defaults={'name': tag_name, 'color': '0d6efd'},
                )
                vm.tags.add(tag)

            ip_value = (server.get('PrimaryIPAddress') or '').strip()
            if ip_value and not vm.primary_ip4:
                iface, _ = VMInterface.objects.get_or_create(
                    virtual_machine=vm, name='eth0',
                )
                address = f'{ip_value}/32'
                ip = IPAddress.objects.filter(address=address).first()
                if not ip:
                    ip = IPAddress(address=address, status='active')
                if not ip.assigned_object_id:
                    ip.assigned_object = iface
                    ip.save()
                    vm.primary_ip4 = ip
                    vm.save()

    def _seed_network(self, site, network):
        """Crée les VLAN, préfixes et passerelles du fichier *.network.json."""
        for vlan_data in network.get('vlans', []):
            vid = vlan_data.get('id')
            if not vid:
                continue
            vlan, created = VLAN.objects.get_or_create(
                vid=vid, site=site,
                defaults={
                    'name': (vlan_data.get('nom') or f'VLAN-{vid}')[:64],
                    'description': (vlan_data.get('description') or '')[:200],
                    'status': 'active',
                },
            )
            if created:
                self.stats['vlans'] += 1

            cidr = (vlan_data.get('network') or '').strip()
            if cidr:
                prefix = Prefix.objects.filter(prefix=cidr).first()
                if not prefix:
                    prefix = Prefix(
                        prefix=cidr,
                        vlan=vlan,
                        status='active',
                        description=(vlan_data.get('description') or '')[:200],
                    )
                    # NetBox ≥ 4.2 : rattachement par « scope », avant : champ site
                    if hasattr(prefix, 'scope'):
                        prefix.scope = site
                    elif hasattr(prefix, 'site'):
                        prefix.site = site
                    prefix.save()
                    self.stats['prefixes'] += 1

            gateway = (vlan_data.get('gateway') or '').strip()
            if gateway:
                address = f'{gateway}/32'
                if not IPAddress.objects.filter(address=address).exists():
                    IPAddress.objects.create(
                        address=address,
                        status='active',
                        role='anycast',
                        description=f"Passerelle {vlan_data.get('nom') or vid}",
                    )

    def _link_servers(self, site, infra, app_index):
        vm_names_by_trigramme = {}
        for server in infra.get('serveurs', []):
            tri = (server.get('trigramme') or '').strip().upper()
            vm_name = (server.get('VM') or '').strip()
            if tri and vm_name:
                vm_names_by_trigramme.setdefault(tri, []).append(vm_name)

        for tri, vm_names in vm_names_by_trigramme.items():
            app = app_index.get(tri)
            if not app:
                continue
            vms = VirtualMachine.objects.filter(name__in=vm_names)
            site_vms = vms.filter(site=site)
            if site_vms.exists():
                vms = site_vms
            for vm in vms:
                if not app.virtual_machines.filter(pk=vm.pk).exists():
                    app.virtual_machines.add(vm)
                    self.stats['vm_links'] += 1

    def _get_or_create_fallback_app(self, site, trigramme):
        """Crée une application hors cartographie (référencée seulement par les flux)."""
        domain, _ = BusinessDomain.objects.get_or_create(
            site=site, name=FALLBACK_DOMAIN,
            defaults={'description': 'Applications référencées uniquement par les flux'},
        )
        process, _ = BusinessProcess.objects.get_or_create(
            domain=domain, name=FALLBACK_PROCESS,
        )
        name = self.trigramme_names.get(trigramme, trigramme)
        app, created = Application.objects.get_or_create(
            process=process, name=name,
            defaults={'trigramme': trigramme},
        )
        if created:
            self.stats['applications'] += 1
            self.stdout.write(f'  Application hors référentiel créée : {name} ({trigramme})')
        return app

    def _import_flux(self, site, flux_data, app_index):
        for flow in flux_data.get('flux', []):
            src_tri = (flow.get('sourceTrigramme') or '').strip().upper()
            dst_tri = (flow.get('targetTrigramme') or '').strip().upper()
            if not src_tri or not dst_tri:
                self.stats['skipped_flows'] += 1
                continue

            source = app_index.get(src_tri)
            if not source:
                source = self._get_or_create_fallback_app(site, src_tri)
                app_index[src_tri] = source
            target = app_index.get(dst_tri)
            if not target:
                target = self._get_or_create_fallback_app(site, dst_tri)
                app_index[dst_tri] = target

            interface_type = INTERFACE_TYPE_MAP.get(
                (flow.get('interfaceType') or '').strip().lower(),
                InterfaceTypeChoices.AUTRE,
            )
            defaults = {
                'source': source,
                'target': target,
                'protocol': (flow.get('protocol') or '')[:50],
                'port': flow.get('port') or None,
                'message_type': (flow.get('messageType') or '')[:50],
                'interface_type': interface_type,
                'eai': (flow.get('eaiName') or '')[:100],
                'description': (flow.get('description') or '')[:200],
            }

            flow_id = (flow.get('id') or '').strip()
            if flow_id:
                _, created = ApplicationFlow.objects.update_or_create(
                    flow_id=flow_id, defaults=defaults,
                )
            else:
                _, created = ApplicationFlow.objects.get_or_create(
                    source=source, target=target,
                    protocol=defaults['protocol'],
                    message_type=defaults['message_type'],
                    defaults=defaults,
                )
            if created:
                self.stats['flows'] += 1

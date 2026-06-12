"""
Applies a modeling bundle (see bundles.py) to a NetBox site: business
structure (domains / processes), sample applications, sample infrastructure
(VLANs, prefixes, gateways, virtual machines) and sample flows.

All operations are idempotent (get_or_create based).
"""
import re

from django.utils.text import slugify

from extras.models import Tag
from ipam.models import IPAddress, Prefix, VLAN
from virtualization.models import VirtualMachine, VMInterface

from .choices import DOMAIN_COLOR_PALETTE
from .models import Application, ApplicationFlow, BusinessDomain, BusinessProcess


def site_prefix(site):
    """Short server-name prefix derived from the site name (e.g. 'CH Val-de-Lys' → 'vdl')."""
    words = re.findall(r'[a-z0-9]+', slugify(site.name))
    if not words:
        return f'site{site.pk}'
    if len(words) == 1:
        return words[0][:4]
    return ''.join(w[0] for w in words[-3:])


def site_net(site):
    """Second IPv4 octet for sample networks, derived from the site PK to avoid collisions."""
    return 10 + (site.pk % 200)


def apply_bundle(site, bundle, with_apps=True, with_infra=True, with_flows=True):
    """Apply a bundle to a site. Returns a stats dict."""
    stats = {
        'domains': 0, 'processes': 0, 'applications': 0,
        'vlans': 0, 'prefixes': 0, 'vms': 0, 'flows': 0,
    }

    # ── Structure: domains and processes ─────────────────────────────────
    process_index = {}
    for idx, dom in enumerate(bundle['domains']):
        domain, created = BusinessDomain.objects.get_or_create(
            site=site, name=dom['name'],
            defaults={
                'description': dom.get('description', '')[:200],
                'color': DOMAIN_COLOR_PALETTE[idx % len(DOMAIN_COLOR_PALETTE)],
            },
        )
        if created:
            stats['domains'] += 1
        for proc in dom['processes']:
            process, created = BusinessProcess.objects.get_or_create(
                domain=domain, name=proc['name'],
                defaults={'description': proc.get('description', '')[:200]},
            )
            if created:
                stats['processes'] += 1
            process_index[(dom['name'], proc['name'])] = process

    app_index = {}
    if with_apps:
        for entry in bundle['applications']:
            interfaces = entry.get('interfaces', [])
            defaults = {
                'description': entry.get('description', '')[:500],
                'editor': entry.get('editor', '')[:100],
                'hosting': (entry.get('hosting') or site.name)[:100],
                'criticality': entry['criticality'],
                'interface_administrative': 'administrative' in interfaces,
                'interface_medicale': 'medicale' in interfaces,
                'interface_facturation': 'facturation' in interfaces,
                'interface_planification': 'planification' in interfaces,
                'interface_autre': 'autre' in interfaces,
            }
            app, created = Application.objects.get_or_create(
                name=entry['name'], defaults=defaults,
            )
            if created:
                stats['applications'] += 1
            process = process_index.get(entry['process'])
            if process:
                app.processes.add(process)
            app_index[entry['key']] = app

    # ── Infrastructure: VLANs, prefixes, gateways, VMs ────────────────────
    if with_infra:
        prefix = site_prefix(site)
        net = site_net(site)

        for vlan_data in bundle.get('vlans', []):
            vlan, created = VLAN.objects.get_or_create(
                vid=vlan_data['vid'], site=site,
                defaults={
                    'name': vlan_data['name'][:64],
                    'description': vlan_data.get('description', '')[:200],
                    'status': 'active',
                },
            )
            if created:
                stats['vlans'] += 1

            cidr = vlan_data['prefix'].format(net=net)
            if not Prefix.objects.filter(prefix=cidr).exists():
                prefix_obj = Prefix(
                    prefix=cidr, vlan=vlan, status='active',
                    description=vlan_data.get('description', '')[:200],
                )
                if hasattr(prefix_obj, 'scope'):
                    prefix_obj.scope = site
                elif hasattr(prefix_obj, 'site'):
                    prefix_obj.site = site
                prefix_obj.save()
                stats['prefixes'] += 1

            gateway = vlan_data.get('gateway', '').format(net=net)
            if gateway and not IPAddress.objects.filter(address=f'{gateway}/32').exists():
                IPAddress.objects.create(
                    address=f'{gateway}/32', status='active', role='anycast',
                    description=f"Gateway {vlan_data['name']}",
                )

        for vm_data in bundle.get('vms', []):
            vm_name = vm_data['name'].format(prefix=prefix)
            vm, created = VirtualMachine.objects.get_or_create(
                name=vm_name, site=site,
                defaults={
                    'status': 'active',
                    'description': vm_data.get('role', '')[:200],
                    'vcpus': vm_data.get('vcpus'),
                    'memory': vm_data.get('memory'),
                    'disk': vm_data.get('disk'),
                },
            )
            if created:
                stats['vms'] += 1

            app = app_index.get(vm_data.get('app'))
            if app:
                app.virtual_machines.add(vm)
                tag_name = f'app:{vm_data["app"]}'
                tag, _ = Tag.objects.get_or_create(
                    slug=slugify(tag_name),
                    defaults={'name': tag_name, 'color': '0d6efd'},
                )
                vm.tags.add(tag)

            ip_value = vm_data.get('ip', '').format(net=net)
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

    # ── Sample flows ──────────────────────────────────────────────────────
    if with_flows and with_apps:
        prefix = site_prefix(site).upper()
        counter = 0
        for flow_data in bundle.get('flows', []):
            source = app_index.get(flow_data['source'])
            target = app_index.get(flow_data['target'])
            if not source or not target:
                continue
            counter += 1
            flow_id = f'{prefix}-FLX-{counter:03d}'
            _, created = ApplicationFlow.objects.get_or_create(
                site=site, source=source, target=target,
                protocol=flow_data.get('protocol', ''),
                message_type=flow_data.get('message_type', ''),
                defaults={
                    'flow_id': flow_id,
                    'port': flow_data.get('port'),
                    'interface_type': flow_data['interface_type'],
                    'eai': flow_data.get('eai', '')[:100],
                    'description': flow_data.get('description', '')[:200],
                },
            )
            if created:
                stats['flows'] += 1

    return stats

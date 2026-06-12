from collections import OrderedDict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views.generic import View
from dcim.models import Site
from netbox.views import generic

from . import filtersets, forms, tables
from .choices import CriticalityChoices, InterfaceTypeChoices, INTERFACE_HEX_COLORS
from .models import Application, ApplicationFlow, BusinessDomain, BusinessProcess


#
# Domaines métier
#

class BusinessDomainListView(generic.ObjectListView):
    queryset = BusinessDomain.objects.select_related('site').annotate(
        process_count=Count('processes', distinct=True),
    )
    table = tables.BusinessDomainTable
    filterset = filtersets.BusinessDomainFilterSet
    filterset_form = forms.BusinessDomainFilterForm


class BusinessDomainView(generic.ObjectView):
    queryset = BusinessDomain.objects.select_related('site')

    def get_extra_context(self, request, instance):
        processes = instance.processes.annotate(
            application_count=Count('applications', distinct=True),
        )
        return {
            'process_table': tables.BusinessProcessTable(processes, exclude=('domain', 'site')),
        }


class BusinessDomainEditView(generic.ObjectEditView):
    queryset = BusinessDomain.objects.all()
    form = forms.BusinessDomainForm


class BusinessDomainDeleteView(generic.ObjectDeleteView):
    queryset = BusinessDomain.objects.all()


class BusinessDomainBulkDeleteView(generic.BulkDeleteView):
    queryset = BusinessDomain.objects.all()
    table = tables.BusinessDomainTable
    filterset = filtersets.BusinessDomainFilterSet


#
# Processus métier
#

class BusinessProcessListView(generic.ObjectListView):
    queryset = BusinessProcess.objects.select_related('domain__site').annotate(
        application_count=Count('applications', distinct=True),
    )
    table = tables.BusinessProcessTable
    filterset = filtersets.BusinessProcessFilterSet
    filterset_form = forms.BusinessProcessFilterForm


class BusinessProcessView(generic.ObjectView):
    queryset = BusinessProcess.objects.select_related('domain__site')

    def get_extra_context(self, request, instance):
        applications = instance.applications.prefetch_related('processes__domain__site')
        return {
            'application_table': tables.ApplicationTable(
                applications, exclude=('processes',),
            ),
        }


class BusinessProcessEditView(generic.ObjectEditView):
    queryset = BusinessProcess.objects.all()
    form = forms.BusinessProcessForm


class BusinessProcessDeleteView(generic.ObjectDeleteView):
    queryset = BusinessProcess.objects.all()


class BusinessProcessBulkDeleteView(generic.BulkDeleteView):
    queryset = BusinessProcess.objects.all()
    table = tables.BusinessProcessTable
    filterset = filtersets.BusinessProcessFilterSet


#
# Applications
#

class ApplicationListView(generic.ObjectListView):
    queryset = Application.objects.prefetch_related('processes__domain__site')
    table = tables.ApplicationTable
    filterset = filtersets.ApplicationFilterSet
    filterset_form = forms.ApplicationFilterForm


class ApplicationView(generic.ObjectView):
    queryset = Application.objects.prefetch_related(
        'processes__domain__site', 'virtual_machines', 'devices',
    )

    def get_extra_context(self, request, instance):
        outbound = instance.flows_as_source.select_related('site', 'source', 'target')
        inbound = instance.flows_as_target.select_related('site', 'source', 'target')
        return {
            'outbound_table': tables.ApplicationFlowTable(outbound, exclude=('source',)),
            'inbound_table': tables.ApplicationFlowTable(inbound, exclude=('target',)),
        }


class ApplicationEditView(generic.ObjectEditView):
    queryset = Application.objects.all()
    form = forms.ApplicationForm


class ApplicationDeleteView(generic.ObjectDeleteView):
    queryset = Application.objects.all()


class ApplicationBulkDeleteView(generic.BulkDeleteView):
    queryset = Application.objects.all()
    table = tables.ApplicationTable
    filterset = filtersets.ApplicationFilterSet


#
# Flux applicatifs
#

class ApplicationFlowListView(generic.ObjectListView):
    queryset = ApplicationFlow.objects.select_related('site', 'source', 'target')
    table = tables.ApplicationFlowTable
    filterset = filtersets.ApplicationFlowFilterSet
    filterset_form = forms.ApplicationFlowFilterForm


class ApplicationFlowView(generic.ObjectView):
    queryset = ApplicationFlow.objects.select_related('site', 'source', 'target')


class ApplicationFlowEditView(generic.ObjectEditView):
    queryset = ApplicationFlow.objects.all()
    form = forms.ApplicationFlowForm


class ApplicationFlowDeleteView(generic.ObjectDeleteView):
    queryset = ApplicationFlow.objects.all()


class ApplicationFlowBulkDeleteView(generic.BulkDeleteView):
    queryset = ApplicationFlow.objects.all()
    table = tables.ApplicationFlowTable
    filterset = filtersets.ApplicationFlowFilterSet


#
# Vues cartographiques (reprises de l'application it-landscape)
#

def _interface_chips(app):
    """Construit les pastilles d'interface (libellé + couleurs) d'une application."""
    mapping = [
        ('interface_administrative', _('Administrative'), InterfaceTypeChoices.ADMINISTRATIVE),
        ('interface_medicale', _('Medical'), InterfaceTypeChoices.MEDICALE),
        ('interface_facturation', _('Billing'), InterfaceTypeChoices.FACTURATION),
        ('interface_planification', _('Scheduling'), InterfaceTypeChoices.PLANIFICATION),
        ('interface_autre', _('Other'), InterfaceTypeChoices.AUTRE),
    ]
    chips = []
    for field, label, key in mapping:
        if getattr(app, field):
            color = INTERFACE_HEX_COLORS[key]
            chips.append({'label': label, 'color': color, 'bg': f'{color}22'})
    return chips


def _landscape_filters(request):
    site_id = request.GET.get('site_id') or ''
    q = (request.GET.get('q') or '').strip()
    criticality = request.GET.get('criticality') or ''
    sites = Site.objects.filter(business_domains__isnull=False).distinct().order_by('name')
    return site_id, q, criticality, sites


class BusinessLandscapeView(LoginRequiredMixin, View):
    """Vue métier : établissements → domaines → processus → applications."""
    template_name = 'netbox_it_landscape/landscape/business.html'

    def get(self, request):
        site_id, q, criticality, sites_choices = _landscape_filters(request)
        view_mode = 'paysage' if request.GET.get('view') == 'paysage' else 'detail'

        applications = Application.objects.prefetch_related('processes__domain__site')
        if site_id:
            applications = applications.filter(processes__domain__site_id=site_id).distinct()
        if criticality:
            applications = applications.filter(criticality=criticality)
        if q:
            applications = applications.filter(
                Q(name__icontains=q)
                | Q(description__icontains=q)
                | Q(editor__icontains=q)
            )

        # Une application multi-site apparaît dans chacun de ses processus
        placements = []
        for app in applications:
            for process in app.processes.all():
                if site_id and str(process.domain.site_id) != str(site_id):
                    continue
                placements.append((process.domain.site, process.domain, process, app))
        placements.sort(key=lambda p: (
            p[0].name.lower(), p[1].name.lower(), p[2].name.lower(), p[3].name.lower(),
        ))

        tree = OrderedDict()
        for site, domain, process, app in placements:
            site_entry = tree.setdefault(site.pk, {
                'site': site, 'domains': OrderedDict(),
                'app_count': 0, 'critical_count': 0,
            })
            domain_entry = site_entry['domains'].setdefault(domain.pk, {
                'domain': domain, 'processes': OrderedDict(),
                'app_count': 0, 'critical_count': 0,
            })
            process_entry = domain_entry['processes'].setdefault(process.pk, {
                'process': process, 'applications': [],
                'critical_count': 0,
            })

            is_critical = app.criticality == CriticalityChoices.CRITICAL
            process_entry['applications'].append({
                'obj': app,
                'is_critical': is_critical,
                'chips': _interface_chips(app),
            })
            if is_critical:
                process_entry['critical_count'] += 1
                domain_entry['critical_count'] += 1
                site_entry['critical_count'] += 1
            domain_entry['app_count'] += 1
            site_entry['app_count'] += 1

        # Conversion en listes pour le template
        sites = []
        for site_entry in tree.values():
            domains = []
            for domain_entry in site_entry['domains'].values():
                domain_entry['processes'] = list(domain_entry['processes'].values())
                domains.append(domain_entry)
            site_entry['domains'] = domains
            sites.append(site_entry)

        return render(request, self.template_name, {
            'sites': sites,
            'sites_choices': sites_choices,
            'criticality_choices': CriticalityChoices.CHOICES,
            'filter_site_id': site_id,
            'filter_q': q,
            'filter_criticality': criticality,
            'view_mode': view_mode,
        })


class ApplicativeLandscapeView(LoginRequiredMixin, View):
    """Vue applicative : une carte par application avec ses serveurs et établissements."""
    template_name = 'netbox_it_landscape/landscape/applicative.html'

    def get(self, request):
        site_id, q, criticality, sites_choices = _landscape_filters(request)

        applications = Application.objects.prefetch_related(
            'processes__domain__site',
            'virtual_machines__primary_ip4', 'virtual_machines__role',
            'devices__primary_ip4', 'devices__role',
        )
        if site_id:
            applications = applications.filter(processes__domain__site_id=site_id).distinct()
        if criticality:
            applications = applications.filter(criticality=criticality)
        if q:
            applications = applications.filter(
                Q(name__icontains=q)
                | Q(description__icontains=q)
                | Q(editor__icontains=q)
                | Q(virtual_machines__name__icontains=q)
                | Q(devices__name__icontains=q)
            ).distinct()

        groups = []
        for app in applications.order_by('name'):
            sites = [site.name for site in app.site_list]
            servers = [
                {
                    'obj': vm,
                    'kind': 'VM',
                    'ip': str(vm.primary_ip4.address.ip) if vm.primary_ip4 else '',
                    'role': vm.role.name if vm.role else '',
                }
                for vm in app.virtual_machines.all()
            ] + [
                {
                    'obj': device,
                    'kind': _('Physical'),
                    'ip': str(device.primary_ip4.address.ip) if device.primary_ip4 else '',
                    'role': device.role.name if device.role else '',
                }
                for device in app.devices.all()
            ]
            groups.append({
                'app': app,
                'name': app.name,
                'sites': sites,
                'is_multi_site': len(sites) > 1,
                'servers': servers,
                'has_critical': app.criticality == CriticalityChoices.CRITICAL,
            })

        return render(request, self.template_name, {
            'groups': groups,
            'sites_choices': sites_choices,
            'criticality_choices': CriticalityChoices.CHOICES,
            'filter_site_id': site_id,
            'filter_q': q,
            'filter_criticality': criticality,
        })


class KpiLandscapeView(LoginRequiredMixin, View):
    """Synthèse KPI : compteurs, points d'attention, répartitions et hubs."""
    template_name = 'netbox_it_landscape/landscape/kpi.html'

    def get(self, request):
        site_id = request.GET.get('site_id') or ''
        sites_choices = Site.objects.filter(business_domains__isnull=False).distinct().order_by('name')

        applications = Application.objects.prefetch_related(
            'processes__domain__site', 'virtual_machines', 'devices',
        )
        flows = ApplicationFlow.objects.select_related('site', 'source', 'target')
        domains = BusinessDomain.objects.all()
        processes = BusinessProcess.objects.all()
        if site_id:
            applications = applications.filter(processes__domain__site_id=site_id).distinct()
            flows = flows.filter(site_id=site_id)
            domains = domains.filter(site_id=site_id)
            processes = processes.filter(domain__site_id=site_id)

        apps = list(applications)
        flows = list(flows)
        total_apps = len(apps)
        total_flows = len(flows)

        def pct(part, total):
            return round(100 * part / total) if total else 0

        # ── Compteurs clés ────────────────────────────────────────────────
        critical_apps = [a for a in apps if a.criticality == CriticalityChoices.CRITICAL]
        multi_apps = [a for a in apps if a.is_multi_site]
        apps_with_servers = [
            a for a in apps
            if len(a.virtual_machines.all()) or len(a.devices.all())
        ]
        kpis = {
            'apps': total_apps,
            'critical': len(critical_apps),
            'critical_pct': pct(len(critical_apps), total_apps),
            'multi': len(multi_apps),
            'multi_pct': pct(len(multi_apps), total_apps),
            'flows': total_flows,
            'server_coverage_pct': pct(len(apps_with_servers), total_apps),
            'domains': domains.count(),
            'processes': processes.count(),
        }

        # ── Points d'attention ────────────────────────────────────────────
        no_server = [a for a in apps if not len(a.virtual_machines.all()) and not len(a.devices.all())]
        attention = [
            {
                'label': _('Critical applications without attached server'),
                'detail': _('Infrastructure incident impact cannot be simulated'),
                'apps': [a for a in no_server if a.criticality == CriticalityChoices.CRITICAL],
                'severity': 'red',
            },
            {
                'label': _('Critical applications without monitoring'),
                'detail': _('No monitoring URL (PRTG, Centreon…) recorded'),
                'apps': [a for a in critical_apps if not a.monitoring_url],
                'severity': 'red',
            },
            {
                'label': _('Applications without business attachment'),
                'detail': _('No associated process — invisible in the business view'),
                'apps': [a for a in apps if not len(a.processes.all())],
                'severity': 'orange',
            },
            {
                'label': _('Applications without contact person'),
                'detail': _('Nobody to call in case of incident'),
                'apps': [a for a in apps if not a.referent],
                'severity': 'orange',
            },
            {
                'label': _('Applications without vendor'),
                'detail': _('Referential quality to complete'),
                'apps': [a for a in apps if not a.editor],
                'severity': 'yellow',
            },
            {
                'label': _('Flows without protocol'),
                'detail': _('Incomplete technical documentation'),
                'apps': [],
                'count_override': len([f for f in flows if not f.protocol]),
                'severity': 'yellow',
            },
        ]
        for item in attention:
            item['count'] = item.get('count_override', len(item['apps']))
            item['preview'] = [a.name for a in item['apps'][:5]]

        # ── Répartition criticité (donut CSS) ─────────────────────────────
        crit_pct = kpis['critical_pct']
        criticality_donut = {
            'critical': len(critical_apps),
            'standard': total_apps - len(critical_apps),
            'pct': crit_pct,
            'gradient': f'#dc2626 0% {crit_pct}%, #64748b {crit_pct}% 100%',
        }

        # ── Flux par type d'interface ─────────────────────────────────────
        interface_counts = OrderedDict()
        for value, label, _color in InterfaceTypeChoices.CHOICES:
            interface_counts[value] = {'label': label, 'count': 0, 'color': INTERFACE_HEX_COLORS[value]}
        for flow in flows:
            if flow.interface_type in interface_counts:
                interface_counts[flow.interface_type]['count'] += 1
        max_iface = max((i['count'] for i in interface_counts.values()), default=0)
        flows_by_interface = [
            {**item, 'pct': pct(item['count'], max_iface)}
            for item in interface_counts.values() if item['count']
        ]

        # ── Dépendance EAI ────────────────────────────────────────────────
        eai_counts = {}
        for flow in flows:
            key = flow.eai.strip() if flow.eai else 'Direct'
            eai_counts[key] = eai_counts.get(key, 0) + 1
        eai_flows = sum(c for name, c in eai_counts.items() if name.lower() != 'direct')
        eai_list = sorted(eai_counts.items(), key=lambda kv: kv[1], reverse=True)
        max_eai = eai_list[0][1] if eai_list else 0
        eai_bars = [
            {'name': name, 'count': count, 'pct': pct(count, max_eai),
             'is_direct': name.lower() == 'direct'}
            for name, count in eai_list[:6]
        ]
        eai_dependency_pct = pct(eai_flows, total_flows)

        # ── Top éditeurs ──────────────────────────────────────────────────
        editor_counts = {}
        for app in apps:
            if app.editor:
                editor_counts[app.editor] = editor_counts.get(app.editor, 0) + 1
        editor_list = sorted(editor_counts.items(), key=lambda kv: kv[1], reverse=True)[:6]
        max_editor = editor_list[0][1] if editor_list else 0
        editor_bars = [
            {'name': name, 'count': count, 'pct': pct(count, max_editor)}
            for name, count in editor_list
        ]

        # ── Top applications connectées (hubs de flux) ────────────────────
        degree = {}
        for flow in flows:
            for app, direction in ((flow.source, 'out'), (flow.target, 'in')):
                entry = degree.setdefault(app.pk, {'app': app, 'in': 0, 'out': 0})
                entry[direction] += 1
        hubs = sorted(degree.values(), key=lambda e: e['in'] + e['out'], reverse=True)[:8]
        max_degree = (hubs[0]['in'] + hubs[0]['out']) if hubs else 0
        for hub in hubs:
            hub['total'] = hub['in'] + hub['out']
            hub['pct'] = pct(hub['total'], max_degree)

        # ── Applications par établissement ────────────────────────────────
        site_counts = OrderedDict()
        for app in apps:
            for site in app.site_list:
                entry = site_counts.setdefault(site.pk, {'site': site, 'count': 0, 'critical': 0})
                entry['count'] += 1
                if app.criticality == CriticalityChoices.CRITICAL:
                    entry['critical'] += 1
        site_bars = sorted(site_counts.values(), key=lambda e: e['count'], reverse=True)
        max_site = site_bars[0]['count'] if site_bars else 0
        for entry in site_bars:
            entry['pct'] = pct(entry['count'], max_site)

        return render(request, self.template_name, {
            'kpis': kpis,
            'attention': attention,
            'criticality_donut': criticality_donut,
            'flows_by_interface': flows_by_interface,
            'eai_bars': eai_bars,
            'eai_dependency_pct': eai_dependency_pct,
            'editor_bars': editor_bars,
            'hubs': hubs,
            'site_bars': site_bars,
            'sites_choices': sites_choices,
            'filter_site_id': site_id,
        })


class FluxLandscapeView(LoginRequiredMixin, View):
    """Vue flux : table filtrable et diagramme source → cible."""
    template_name = 'netbox_it_landscape/landscape/flux.html'

    NODE_HEIGHT = 34
    NODE_GAP = 22
    NODE_WIDTH = 230
    SVG_WIDTH = 1100
    LABEL_MAX = 28

    def get(self, request):
        site_id = request.GET.get('site_id') or ''
        q = (request.GET.get('q') or '').strip()
        interface_type = request.GET.get('interface_type') or ''
        protocol = request.GET.get('protocol') or ''
        eai = request.GET.get('eai') or ''

        flows = ApplicationFlow.objects.select_related('site', 'source', 'target')
        if site_id:
            flows = flows.filter(site_id=site_id)
        if interface_type:
            flows = flows.filter(interface_type=interface_type)
        if protocol:
            flows = flows.filter(protocol__iexact=protocol)
        if eai:
            flows = flows.filter(eai__iexact=eai)
        if q:
            flows = flows.filter(
                Q(flow_id__icontains=q)
                | Q(description__icontains=q)
                | Q(message_type__icontains=q)
                | Q(source__name__icontains=q)
                | Q(target__name__icontains=q)
            )
        flows = list(flows.order_by('flow_id', 'id'))

        svg = self._build_diagram(flows)

        all_flows = ApplicationFlow.objects.all()
        protocols = sorted(set(all_flows.values_list('protocol', flat=True)) - {''})
        eais = sorted(set(all_flows.values_list('eai', flat=True)) - {''})
        sites_choices = Site.objects.filter(business_domains__isnull=False).distinct().order_by('name')

        legend = [
            {'label': choice[1], 'color': INTERFACE_HEX_COLORS[choice[0]]}
            for choice in InterfaceTypeChoices.CHOICES
        ]

        return render(request, self.template_name, {
            'flows': flows,
            'svg': svg,
            'sites_choices': sites_choices,
            'interface_choices': InterfaceTypeChoices.CHOICES,
            'protocols': protocols,
            'eais': eais,
            'legend': legend,
            'filter_site_id': site_id,
            'filter_q': q,
            'filter_interface_type': interface_type,
            'filter_protocol': protocol,
            'filter_eai': eai,
        })

    def _build_diagram(self, flows):
        """Diagramme bipartite : applications sources à gauche, cibles à droite."""
        if not flows:
            return None

        def label(app):
            return app.name

        def display(name):
            if len(name) > self.LABEL_MAX:
                return name[:self.LABEL_MAX - 1] + '…'
            return name

        sources, targets = [], []
        for flow in flows:
            src, dst = label(flow.source), label(flow.target)
            if src not in sources:
                sources.append(src)
            if dst not in targets:
                targets.append(dst)
        sources.sort(key=str.lower)
        targets.sort(key=str.lower)

        step = self.NODE_HEIGHT + self.NODE_GAP
        left_x = 10
        right_x = self.SVG_WIDTH - self.NODE_WIDTH - 10
        edge_x1 = left_x + self.NODE_WIDTH
        edge_x2 = right_x
        mid_x = self.SVG_WIDTH // 2

        left_nodes = [
            {'label': name, 'display': display(name), 'x': left_x, 'y': 20 + i * step}
            for i, name in enumerate(sources)
        ]
        right_nodes = [
            {'label': name, 'display': display(name), 'x': right_x, 'y': 20 + i * step}
            for i, name in enumerate(targets)
        ]
        left_index = {node['label']: node for node in left_nodes}
        right_index = {node['label']: node for node in right_nodes}

        edges = []
        for flow in flows:
            src_node = left_index[label(flow.source)]
            dst_node = right_index[label(flow.target)]
            y1 = src_node['y'] + self.NODE_HEIGHT // 2
            y2 = dst_node['y'] + self.NODE_HEIGHT // 2
            parts = [p for p in (flow.protocol, flow.message_type, flow.eai) if p]
            edges.append({
                'x1': edge_x1, 'y1': y1,
                'x2': edge_x2, 'y2': y2,
                'cx': mid_x,
                'color': INTERFACE_HEX_COLORS.get(flow.interface_type, '#9e9e9e'),
                'title': f"{flow} — {' · '.join(parts)}" if parts else str(flow),
            })

        height = 40 + step * max(len(sources), len(targets))
        return {
            'width': self.SVG_WIDTH,
            'height': height,
            'node_width': self.NODE_WIDTH,
            'node_height': self.NODE_HEIGHT,
            'left_nodes': left_nodes,
            'right_nodes': right_nodes,
            'edges': edges,
        }


class SetupWizardView(LoginRequiredMixin, View):
    """Setup wizard: apply a sector modeling bundle to a (new or existing) site."""
    template_name = 'netbox_it_landscape/landscape/wizard.html'

    def _check_permission(self, request):
        return request.user.has_perm('netbox_it_landscape.add_businessdomain')

    def _bundle_cards(self):
        from .bundles import BUNDLES
        return [
            {
                'key': key,
                'label': bundle['label'],
                'description': bundle['description'],
                'icon': bundle.get('icon', 'mdi-sitemap'),
                'domain_count': len(bundle['domains']),
                'process_count': sum(len(d['processes']) for d in bundle['domains']),
                'app_count': len(bundle['applications']),
                'vm_count': len(bundle.get('vms', [])),
                'vlan_count': len(bundle.get('vlans', [])),
                'flow_count': len(bundle.get('flows', [])),
            }
            for key, bundle in BUNDLES.items()
        ]

    def get(self, request):
        from .forms import SetupWizardForm
        if not self._check_permission(request):
            return render(request, self.template_name, {'forbidden': True}, status=403)
        return render(request, self.template_name, {
            'form': SetupWizardForm(),
            'bundles': self._bundle_cards(),
        })

    def post(self, request):
        from django.utils.text import slugify
        from .bundles import BUNDLES
        from .forms import SetupWizardForm
        from .seeding import apply_bundle

        if not self._check_permission(request):
            return render(request, self.template_name, {'forbidden': True}, status=403)

        form = SetupWizardForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {
                'form': form,
                'bundles': self._bundle_cards(),
            })

        bundle = BUNDLES[form.cleaned_data['bundle']]
        site_name = form.cleaned_data['site_name'].strip()
        site = Site.objects.filter(name__iexact=site_name).first()
        site_created = False
        if not site:
            site = Site.objects.create(
                name=site_name,
                slug=slugify(site_name)[:100],
                status='active',
            )
            site_created = True

        stats = apply_bundle(
            site, bundle,
            with_apps=form.cleaned_data['with_apps'],
            with_infra=form.cleaned_data['with_infra'],
            with_flows=form.cleaned_data['with_flows'],
        )

        return render(request, self.template_name, {
            'form': SetupWizardForm(),
            'bundles': self._bundle_cards(),
            'result': {
                'site': site,
                'site_created': site_created,
                'bundle_label': bundle['label'],
                'stats': stats,
            },
        })


class ComparisonLandscapeView(LoginRequiredMixin, View):
    """Facility comparison: similarity matrix and mutualization opportunities."""
    template_name = 'netbox_it_landscape/landscape/comparison.html'

    def get(self, request):
        all_sites = list(
            Site.objects.filter(business_domains__isnull=False).distinct().order_by('name')
        )
        selected_ids = request.GET.getlist('site_id')
        if selected_ids:
            sites = [s for s in all_sites if str(s.pk) in selected_ids]
        else:
            sites = all_sites
        if len(sites) < 2:
            sites = all_sites

        site_pks = {s.pk for s in sites}
        applications = Application.objects.prefetch_related('processes__domain__site')

        # Application → deployed sites / process names (restricted to selection)
        app_entries = []
        apps_by_site = {s.pk: set() for s in sites}
        process_map = {}  # normalized process name → {site_pk: set(app names)}
        for app in applications:
            deployed = set()
            for process in app.processes.all():
                spk = process.domain.site_id
                if spk not in site_pks:
                    continue
                deployed.add(spk)
                apps_by_site[spk].add(app.pk)
                key = process.name.strip().lower()
                entry = process_map.setdefault(key, {'label': process.name, 'sites': {}})
                entry['sites'].setdefault(spk, set()).add(app.name)
            if deployed:
                app_entries.append({'app': app, 'site_pks': deployed})

        def jaccard(a, b):
            union = a | b
            if not union:
                return 0
            return round(100 * len(a & b) / len(union))

        # Similarity matrix
        matrix = []
        pair_scores = []
        for site_a in sites:
            cells = []
            for site_b in sites:
                if site_a.pk == site_b.pk:
                    cells.append({'self': True})
                    continue
                score = jaccard(apps_by_site[site_a.pk], apps_by_site[site_b.pk])
                common = len(apps_by_site[site_a.pk] & apps_by_site[site_b.pk])
                cells.append({'self': False, 'score': score, 'common': common, 'other': site_b})
                if site_a.pk < site_b.pk:
                    pair_scores.append(score)
            matrix.append({'site': site_a, 'cells': cells, 'count': len(apps_by_site[site_a.pk])})

        avg_similarity = round(sum(pair_scores) / len(pair_scores)) if pair_scores else 0

        # Already mutualized: applications deployed on ≥ 2 selected sites
        mutualized = sorted(
            (e for e in app_entries if len(e['site_pks']) > 1),
            key=lambda e: (-len(e['site_pks']), e['app'].name.lower()),
        )
        site_names = {s.pk: s.name for s in sites}
        for entry in mutualized:
            entry['sites'] = sorted(site_names[pk] for pk in entry['site_pks'])
            entry['coverage'] = round(100 * len(entry['site_pks']) / len(sites)) if sites else 0

        # Mutualization opportunities: same process, different applications
        opportunities = []
        for entry in process_map.values():
            per_site = entry['sites']
            if len(per_site) < 2:
                continue
            app_sets = list(per_site.values())
            if all(s == app_sets[0] for s in app_sets[1:]):
                continue  # already harmonized
            opportunities.append({
                'process': entry['label'],
                'columns': [
                    {'site': site_names[pk], 'apps': sorted(apps)}
                    for pk, apps in sorted(per_site.items(), key=lambda kv: site_names[kv[0]])
                ],
                'distinct_apps': len(set().union(*app_sets)),
            })
        opportunities.sort(key=lambda o: (-o['distinct_apps'], o['process'].lower()))

        # Site-specific applications (deployed on exactly one selected site)
        unique_by_site = {s.pk: [] for s in sites}
        for entry in app_entries:
            if len(entry['site_pks']) == 1:
                unique_by_site[next(iter(entry['site_pks']))].append(entry['app'])
        unique_panels = [
            {'site': s, 'apps': sorted(unique_by_site[s.pk], key=lambda a: a.name.lower())}
            for s in sites
        ]

        return render(request, self.template_name, {
            'all_sites': all_sites,
            'sites': sites,
            'selected_ids': [str(s.pk) for s in sites],
            'matrix': matrix,
            'avg_similarity': avg_similarity,
            'mutualized': mutualized,
            'mutualized_count': len(mutualized),
            'opportunities': opportunities,
            'unique_panels': unique_panels,
        })

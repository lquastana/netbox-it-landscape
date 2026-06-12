from collections import OrderedDict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.shortcuts import render
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
        applications = instance.applications.select_related('process__domain__site')
        return {
            'application_table': tables.ApplicationTable(
                applications, exclude=('process', 'domain', 'site'),
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
    queryset = Application.objects.select_related('process__domain__site')
    table = tables.ApplicationTable
    filterset = filtersets.ApplicationFilterSet
    filterset_form = forms.ApplicationFilterForm


class ApplicationView(generic.ObjectView):
    queryset = Application.objects.select_related('process__domain__site').prefetch_related(
        'virtual_machines', 'devices',
    )

    def get_extra_context(self, request, instance):
        outbound = instance.flows_as_source.select_related(
            'source__process__domain__site', 'target__process__domain__site',
        )
        inbound = instance.flows_as_target.select_related(
            'source__process__domain__site', 'target__process__domain__site',
        )
        return {
            'outbound_table': tables.ApplicationFlowTable(outbound, exclude=('source', 'site')),
            'inbound_table': tables.ApplicationFlowTable(inbound, exclude=('target', 'site')),
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
    queryset = ApplicationFlow.objects.select_related(
        'source__process__domain__site', 'target__process__domain__site',
    )
    table = tables.ApplicationFlowTable
    filterset = filtersets.ApplicationFlowFilterSet
    filterset_form = forms.ApplicationFlowFilterForm


class ApplicationFlowView(generic.ObjectView):
    queryset = ApplicationFlow.objects.select_related(
        'source__process__domain__site', 'target__process__domain__site',
    )


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
        ('interface_administrative', 'Administrative', InterfaceTypeChoices.ADMINISTRATIVE),
        ('interface_medicale', 'Médicale', InterfaceTypeChoices.MEDICALE),
        ('interface_facturation', 'Facturation', InterfaceTypeChoices.FACTURATION),
        ('interface_planification', 'Planification', InterfaceTypeChoices.PLANIFICATION),
        ('interface_autre', 'Autre', InterfaceTypeChoices.AUTRE),
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

        applications = Application.objects.select_related('process__domain__site')
        if site_id:
            applications = applications.filter(process__domain__site_id=site_id)
        if criticality:
            applications = applications.filter(criticality=criticality)
        if q:
            applications = applications.filter(
                Q(name__icontains=q)
                | Q(trigramme__icontains=q)
                | Q(description__icontains=q)
                | Q(editor__icontains=q)
            )

        tree = OrderedDict()
        for app in applications.order_by(
            'process__domain__site__name', 'process__domain__name', 'process__name', 'name',
        ):
            site = app.process.domain.site
            domain = app.process.domain
            process = app.process

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
        })


class ApplicativeLandscapeView(LoginRequiredMixin, View):
    """Vue applicative : applications regroupées par trigramme avec serveurs associés."""
    template_name = 'netbox_it_landscape/landscape/applicative.html'

    def get(self, request):
        site_id, q, criticality, sites_choices = _landscape_filters(request)

        applications = Application.objects.select_related(
            'process__domain__site',
        ).prefetch_related(
            'virtual_machines__primary_ip4', 'virtual_machines__role',
            'devices__primary_ip4', 'devices__role',
        )
        if site_id:
            applications = applications.filter(process__domain__site_id=site_id)
        if criticality:
            applications = applications.filter(criticality=criticality)
        if q:
            applications = applications.filter(
                Q(name__icontains=q)
                | Q(trigramme__icontains=q)
                | Q(description__icontains=q)
                | Q(editor__icontains=q)
                | Q(virtual_machines__name__icontains=q)
                | Q(devices__name__icontains=q)
            ).distinct()

        groups = OrderedDict()
        for app in applications.order_by('trigramme', 'name'):
            key = app.trigramme or '—'
            group = groups.setdefault(key, {
                'trigramme': key,
                'name': app.name,
                'apps': [],
                'sites': [],
                'servers': [],
                'server_keys': set(),
                'has_critical': False,
            })
            group['apps'].append(app)
            site_name = app.process.domain.site.name
            if site_name not in group['sites']:
                group['sites'].append(site_name)
            if app.criticality == CriticalityChoices.CRITICAL:
                group['has_critical'] = True

            for vm in app.virtual_machines.all():
                if ('vm', vm.pk) in group['server_keys']:
                    continue
                group['server_keys'].add(('vm', vm.pk))
                group['servers'].append({
                    'obj': vm,
                    'kind': 'VM',
                    'ip': str(vm.primary_ip4.address.ip) if vm.primary_ip4 else '',
                    'role': vm.role.name if vm.role else '',
                })
            for device in app.devices.all():
                if ('device', device.pk) in group['server_keys']:
                    continue
                group['server_keys'].add(('device', device.pk))
                group['servers'].append({
                    'obj': device,
                    'kind': 'Physique',
                    'ip': str(device.primary_ip4.address.ip) if device.primary_ip4 else '',
                    'role': device.role.name if device.role else '',
                })

        for group in groups.values():
            del group['server_keys']

        return render(request, self.template_name, {
            'groups': list(groups.values()),
            'sites_choices': sites_choices,
            'criticality_choices': CriticalityChoices.CHOICES,
            'filter_site_id': site_id,
            'filter_q': q,
            'filter_criticality': criticality,
        })


class FluxLandscapeView(LoginRequiredMixin, View):
    """Vue flux : table filtrable et diagramme source → cible."""
    template_name = 'netbox_it_landscape/landscape/flux.html'

    NODE_HEIGHT = 34
    NODE_GAP = 22
    NODE_WIDTH = 150
    SVG_WIDTH = 920

    def get(self, request):
        site_id = request.GET.get('site_id') or ''
        q = (request.GET.get('q') or '').strip()
        interface_type = request.GET.get('interface_type') or ''
        protocol = request.GET.get('protocol') or ''
        eai = request.GET.get('eai') or ''

        flows = ApplicationFlow.objects.select_related(
            'source__process__domain__site', 'target__process__domain__site',
        )
        if site_id:
            flows = flows.filter(source__process__domain__site_id=site_id)
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
                | Q(source__trigramme__icontains=q)
                | Q(source__name__icontains=q)
                | Q(target__trigramme__icontains=q)
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
            return app.trigramme or app.name[:12]

        sources, targets = [], []
        for flow in flows:
            src, dst = label(flow.source), label(flow.target)
            if src not in sources:
                sources.append(src)
            if dst not in targets:
                targets.append(dst)
        sources.sort()
        targets.sort()

        step = self.NODE_HEIGHT + self.NODE_GAP
        left_x = 10
        right_x = self.SVG_WIDTH - self.NODE_WIDTH - 10
        edge_x1 = left_x + self.NODE_WIDTH
        edge_x2 = right_x
        mid_x = self.SVG_WIDTH // 2

        left_nodes = [
            {'label': name, 'x': left_x, 'y': 20 + i * step}
            for i, name in enumerate(sources)
        ]
        right_nodes = [
            {'label': name, 'x': right_x, 'y': 20 + i * step}
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

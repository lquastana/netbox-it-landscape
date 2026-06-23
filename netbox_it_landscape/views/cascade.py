from collections import defaultdict

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy
from django.views import View

from ..models import Application, ApplicationFlow

# ── Incident status model ──────────────────────────────────────────────────────

STATUS_RANK = {'hs': 4, 'degrade': 3, 'intermittent': 2, 'latence': 1}

# Display labels are resolved lazily, in the active request language.
STATUS_LABELS = {
    'hs': gettext_lazy('Down'),
    'degrade': gettext_lazy('Degraded'),
    'latence': gettext_lazy('Latency'),
    'intermittent': gettext_lazy('Intermittent'),
}
STATUS_COLORS = {
    'hs': 'red',
    'degrade': 'orange',
    'latence': 'blue',
    'intermittent': 'purple',
}

# Cause codes are stable internal identifiers; their display labels are translated.
CAUSE_LABELS = {
    'app': gettext_lazy('Application'),
    'infra': gettext_lazy('Infrastructure'),
    'flow': gettext_lazy('Flow'),
    'flow_out': gettext_lazy('Outbound flow'),
    'hosting': gettext_lazy('Hosting provider'),
    'propagation': gettext_lazy('Upstream dependency'),
}


def merge_status(current, incoming):
    if not current:
        return incoming
    return incoming if STATUS_RANK.get(incoming, 0) > STATUS_RANK.get(current, 0) else current


def map_indirect_status(status):
    return 'degrade' if status == 'hs' else status


def propagate_status(status, depth, interface_type=''):
    """Attenuate the status as it propagates through flows, by depth and interface type."""
    if depth >= 5:
        return None
    is_sync = any(
        kw in (interface_type or '').lower()
        for kw in ('sync', 'temps réel', 'eai', 'middleware', 'api', 'hl7', 'fhir', 'dicom')
    )
    rank = STATUS_RANK.get(status, 0)
    if depth == 0:
        return status
    if depth == 1:
        if is_sync:
            return map_indirect_status(status)
        return 'latence' if rank >= STATUS_RANK['degrade'] else None
    if rank >= STATUS_RANK['degrade']:
        return 'latence'
    return None


def actions_for_status(status, cause_codes):
    """Return a deduplicated list of recommended actions, translated to the active language."""
    actions = []
    if status == 'hs':
        actions.append(_('Trigger the DRP/BCP if available'))
        actions.append(_('Notify IT management and support teams'))
    if 'infra' in cause_codes:
        actions.append(_('Check the server status (monitoring, system logs)'))
        if status == 'hs':
            actions.append(_('Fail over to the backup server or restart'))
    if 'flow' in cause_codes or 'flow_out' in cause_codes:
        actions.append(_('Check the middleware / interface availability'))
        actions.append(_('Enable degraded mode without the dependent flows'))
    if 'hosting' in cause_codes:
        actions.append(_('Contact the hosting provider and get a recovery ETA'))
        actions.append(_('Review the contractual SLA commitments'))
    if 'propagation' in cause_codes:
        actions.append(_('Identify and address the source component first'))
        actions.append(_('Enable a manual data-entry fallback if possible'))
    if status in ('degrade', 'latence'):
        actions.append(_('Prioritise critical flows and processes'))
        actions.append(_('Inform users of the degraded mode'))
    if status == 'intermittent':
        actions.append(_('Analyse logs to identify the instability pattern'))
    return list(dict.fromkeys(actions))


# ── Cascade impact simulator ────────────────────────────────────────────────────

class CascadeSimulatorView(PermissionRequiredMixin, View):
    permission_required = 'netbox_it_landscape.view_application'
    template_name = 'netbox_it_landscape/cascade/simulator.html'

    def _run_analysis(self, selected_components):
        """
        BFS cascade propagation through ApplicationFlow links.
        selected_components: list of dicts {type, obj_id, status, label}
        """
        all_flows = list(ApplicationFlow.objects.select_related('source', 'target').all())
        outgoing = defaultdict(list)
        for flow in all_flows:
            outgoing[flow.source_id].append(flow)

        app_cache = {
            a.pk: a
            for a in Application.objects.prefetch_related('processes__domain__site').all()
        }

        impacted_apps = {}

        def add_app_impact(app_id, status, cause, depth):
            current = impacted_apps.get(app_id)
            merged = merge_status(current['status'] if current else None, status)
            causes = list(current['causes']) if current else []
            if cause and not any(c['label'] == cause['label'] for c in causes):
                causes.append(cause)
            new_depth = min(depth, current['depth']) if current else depth
            changed = not current or merged != current['status'] or depth < current['depth']
            impacted_apps[app_id] = {
                'app_id': app_id,
                'status': merged,
                'causes': causes,
                'depth': new_depth,
            }
            return changed

        for comp in selected_components:
            status = comp['status']
            ct = comp['type']
            label = comp['label']

            if ct == 'application':
                if comp['obj_id'] in app_cache:
                    add_app_impact(comp['obj_id'], status,
                                   {'code': 'app', 'label': label}, 0)

            elif ct in ('vm', 'device'):
                if ct == 'vm':
                    apps = Application.objects.filter(virtual_machines__id=comp['obj_id'])
                else:
                    apps = Application.objects.filter(devices__id=comp['obj_id'])
                for app in apps:
                    add_app_impact(app.pk, status,
                                   {'code': 'infra', 'label': label}, 0)

            elif ct == 'flow':
                flow_obj = ApplicationFlow.objects.filter(pk=comp['obj_id']).first()
                if flow_obj:
                    tgt_status = propagate_status(status, 1, flow_obj.interface_type) or 'latence'
                    add_app_impact(flow_obj.target_id, tgt_status,
                                   {'code': 'flow', 'label': label}, 0)
                    src_status = map_indirect_status(tgt_status)
                    add_app_impact(flow_obj.source_id, src_status,
                                   {'code': 'flow_out', 'label': label}, 0)

            elif ct == 'hosting':
                hosting_val = comp.get('hosting_value', '')
                for app in Application.objects.filter(hosting=hosting_val):
                    add_app_impact(app.pk, status,
                                   {'code': 'hosting', 'label': label}, 0)

        # BFS propagation through flows
        visited = set()
        queue = list(impacted_apps.values())
        while queue:
            current = queue.pop(0)
            key = f"{current['app_id']}:{current['depth']}"
            if key in visited:
                continue
            visited.add(key)
            for flow in outgoing.get(current['app_id'], []):
                prop = propagate_status(current['status'], current['depth'] + 1, flow.interface_type)
                if not prop:
                    continue
                src = app_cache.get(flow.source_id, flow.source)
                tgt = app_cache.get(flow.target_id, flow.target)
                changed = add_app_impact(
                    flow.target_id, prop,
                    {'code': 'propagation', 'label': f'{src.name} → {tgt.name}'},
                    current['depth'] + 1,
                )
                if changed:
                    queue.append(impacted_apps[flow.target_id])

        # Build per-process rows
        impacted_app_rows = []
        impacted_process_rows = []
        for app_id, impact in impacted_apps.items():
            app = app_cache.get(app_id)
            if not app:
                continue
            processes = list(app.processes.all())
            cause_codes = {c['code'] for c in impact['causes']}
            # Decorate causes with translated display labels
            display_causes = [
                {'type': CAUSE_LABELS.get(c['code'], c['code']), 'label': c['label']}
                for c in impact['causes']
            ]
            row = {
                'app': app,
                'status': impact['status'],
                'status_label': STATUS_LABELS.get(impact['status'], impact['status']),
                'status_color': STATUS_COLORS.get(impact['status'], 'secondary'),
                'causes': display_causes,
                'depth': impact['depth'],
                'processes': processes,
                'rank': STATUS_RANK.get(impact['status'], 0),
                'actions': actions_for_status(impact['status'], cause_codes),
            }
            impacted_app_rows.append(row)
            for proc in processes:
                impacted_process_rows.append({**row, 'process': proc,
                                              'site': proc.domain.site,
                                              'domain': proc.domain})

        impacted_app_rows.sort(key=lambda r: (-r['rank'], r['depth'], r['app'].name))
        impacted_process_rows.sort(key=lambda r: (-r['rank'], r['depth'], r['process'].name))

        severe_ids = {
            app_id for app_id, imp in impacted_apps.items()
            if STATUS_RANK.get(imp['status'], 0) >= STATUS_RANK['degrade']
        }
        blocked_flows = [
            f for f in all_flows
            if f.source_id in severe_ids or f.target_id in severe_ids
        ]

        by_site = defaultdict(list)
        for row in impacted_process_rows:
            by_site[row['site']].append(row)

        return {
            'impacted_apps': impacted_app_rows,
            'impacted_processes': impacted_process_rows,
            'blocked_flows': blocked_flows,
            'by_site': dict(by_site),
            'total_apps': len(impacted_app_rows),
            'total_processes': len(impacted_process_rows),
            'total_flows': len(blocked_flows),
        }

    def get(self, request):
        from dcim.models import Device
        from virtualization.models import VirtualMachine

        applications = Application.objects.order_by('name')
        flows = ApplicationFlow.objects.select_related('source', 'target').order_by('flow_id', 'source__name')
        hosting_values = (
            Application.objects.exclude(hosting='')
            .values_list('hosting', flat=True)
            .distinct()
            .order_by('hosting')
        )
        vms = VirtualMachine.objects.filter(
            it_landscape_applications__isnull=False,
        ).distinct().order_by('name')
        devices = Device.objects.filter(
            it_landscape_applications__isnull=False,
        ).distinct().order_by('name')

        selected_components = []
        analysis = None

        comp_types = request.GET.getlist('comp_type')
        comp_ids = request.GET.getlist('comp_id')
        comp_statuses = request.GET.getlist('comp_status')
        comp_labels = request.GET.getlist('comp_label')

        for ct, ci, cs, cl in zip(comp_types, comp_ids, comp_statuses, comp_labels):
            comp = {'type': ct, 'status': cs, 'label': cl}
            if ct == 'hosting':
                comp['hosting_value'] = ci
                comp['obj_id'] = None
            else:
                comp['obj_id'] = int(ci) if ci.isdigit() else None
            selected_components.append(comp)

        if selected_components:
            analysis = self._run_analysis(selected_components)

        return render(request, self.template_name, {
            'applications': applications,
            'flows': flows,
            'hosting_values': hosting_values,
            'vms': vms,
            'devices': devices,
            'selected_components': selected_components,
            'analysis': analysis,
            'status_options': [
                ('hs', _('Down — unavailable')),
                ('degrade', _('Degraded')),
                ('latence', _('Latency')),
                ('intermittent', _('Intermittent')),
            ],
        })

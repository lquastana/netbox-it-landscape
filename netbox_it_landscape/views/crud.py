from django.db.models import Count
from netbox.views import generic

from .. import filtersets, forms, tables
from ..models import Application, ApplicationFlow, BusinessDomain, BusinessProcess

#
# Business domains
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
# Business processes
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
# Application flows
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

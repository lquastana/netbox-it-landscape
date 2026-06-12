import django_filters
from django.db.models import Q
from dcim.models import Site
from netbox.filtersets import NetBoxModelFilterSet

from .choices import CriticalityChoices, InterfaceTypeChoices
from .models import Application, ApplicationFlow, BusinessDomain, BusinessProcess


class BusinessDomainFilterSet(NetBoxModelFilterSet):
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name='site',
        queryset=Site.objects.all(),
        label='Établissement (ID)',
    )

    class Meta:
        model = BusinessDomain
        fields = ('id', 'name')

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | Q(description__icontains=value)
        )


class BusinessProcessFilterSet(NetBoxModelFilterSet):
    domain_id = django_filters.ModelMultipleChoiceFilter(
        field_name='domain',
        queryset=BusinessDomain.objects.all(),
        label='Domaine (ID)',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name='domain__site',
        queryset=Site.objects.all(),
        label='Établissement (ID)',
    )

    class Meta:
        model = BusinessProcess
        fields = ('id', 'name')

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | Q(description__icontains=value)
        )


class ApplicationFilterSet(NetBoxModelFilterSet):
    process_id = django_filters.ModelMultipleChoiceFilter(
        field_name='processes',
        queryset=BusinessProcess.objects.all(),
        label='Processus (ID)',
    )
    domain_id = django_filters.ModelMultipleChoiceFilter(
        field_name='processes__domain',
        queryset=BusinessDomain.objects.all(),
        label='Domaine (ID)',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name='processes__domain__site',
        queryset=Site.objects.all(),
        label='Établissement (ID)',
    )
    criticality = django_filters.MultipleChoiceFilter(
        choices=CriticalityChoices,
    )

    class Meta:
        model = Application
        fields = ('id', 'name', 'editor', 'hosting')

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(description__icontains=value)
            | Q(editor__icontains=value)
        )


class ApplicationFlowFilterSet(NetBoxModelFilterSet):
    source_id = django_filters.ModelMultipleChoiceFilter(
        field_name='source',
        queryset=Application.objects.all(),
        label='Application source (ID)',
    )
    target_id = django_filters.ModelMultipleChoiceFilter(
        field_name='target',
        queryset=Application.objects.all(),
        label='Application cible (ID)',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name='site',
        queryset=Site.objects.all(),
        label='Établissement (ID)',
    )
    interface_type = django_filters.MultipleChoiceFilter(
        choices=InterfaceTypeChoices,
    )

    class Meta:
        model = ApplicationFlow
        fields = ('id', 'flow_id', 'protocol', 'port', 'message_type', 'eai')

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(flow_id__icontains=value)
            | Q(protocol__icontains=value)
            | Q(message_type__icontains=value)
            | Q(eai__icontains=value)
            | Q(description__icontains=value)
            | Q(source__name__icontains=value)
            | Q(target__name__icontains=value)
        )

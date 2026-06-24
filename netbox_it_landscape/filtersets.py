import django_filters
from dcim.models import Site
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from netbox.filtersets import NetBoxModelFilterSet

from .choices import (
    AuthenticationModeChoices,
    CriticalityChoices,
    InterfaceTypeChoices,
)
from .models import (
    Application,
    ApplicationFlow,
    BusinessDomain,
    BusinessProcess,
)


class BusinessDomainFilterSet(NetBoxModelFilterSet):
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name='site',
        queryset=Site.objects.all(),
        label=_('Establishment (ID)'),
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
        label=_('Domain (ID)'),
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name='domain__site',
        queryset=Site.objects.all(),
        label=_('Establishment (ID)'),
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
        label=_('Process (ID)'),
    )
    domain_id = django_filters.ModelMultipleChoiceFilter(
        field_name='processes__domain',
        queryset=BusinessDomain.objects.all(),
        label=_('Domain (ID)'),
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name='processes__domain__site',
        queryset=Site.objects.all(),
        label=_('Establishment (ID)'),
    )
    criticality = django_filters.MultipleChoiceFilter(
        choices=CriticalityChoices,
    )
    authentication_modes = django_filters.MultipleChoiceFilter(
        choices=AuthenticationModeChoices,
        method='filter_authentication_modes',
        label=_('Authentication modes'),
    )
    authentication_primary = django_filters.MultipleChoiceFilter(
        choices=AuthenticationModeChoices,
        label=_('Primary authentication mode'),
    )
    authentication_maintained = django_filters.BooleanFilter(
        label=_('Authentication mapping maintained'),
    )
    authentication_documented = django_filters.BooleanFilter(
        method='filter_authentication_documented',
        label=_('Authentication documented'),
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

    def filter_authentication_modes(self, queryset, name, value):
        """Applications exposing any of the selected modes (ArrayField contains)."""
        if not value:
            return queryset
        q = Q()
        for mode in value:
            q |= Q(authentication_modes__contains=[mode])
        return queryset.filter(q)

    def filter_authentication_documented(self, queryset, name, value):
        """Applications with at least one mapped authentication mode (PROC-09A)."""
        documented = Q(authentication_modes__len__gt=0)
        if value:
            return queryset.filter(documented)
        return queryset.exclude(documented)


class ApplicationFlowFilterSet(NetBoxModelFilterSet):
    source_id = django_filters.ModelMultipleChoiceFilter(
        field_name='source',
        queryset=Application.objects.all(),
        label=_('Source application (ID)'),
    )
    target_id = django_filters.ModelMultipleChoiceFilter(
        field_name='target',
        queryset=Application.objects.all(),
        label=_('Target application (ID)'),
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name='site',
        queryset=Site.objects.all(),
        label=_('Establishment (ID)'),
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

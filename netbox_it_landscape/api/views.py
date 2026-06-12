from netbox.api.viewsets import NetBoxModelViewSet

from .. import filtersets
from ..models import Application, ApplicationFlow, BusinessDomain, BusinessProcess
from . import serializers


class BusinessDomainViewSet(NetBoxModelViewSet):
    queryset = BusinessDomain.objects.select_related('site').prefetch_related('tags')
    serializer_class = serializers.BusinessDomainSerializer
    filterset_class = filtersets.BusinessDomainFilterSet


class BusinessProcessViewSet(NetBoxModelViewSet):
    queryset = BusinessProcess.objects.select_related('domain__site').prefetch_related('tags')
    serializer_class = serializers.BusinessProcessSerializer
    filterset_class = filtersets.BusinessProcessFilterSet


class ApplicationViewSet(NetBoxModelViewSet):
    queryset = Application.objects.prefetch_related(
        'processes__domain__site', 'virtual_machines', 'devices', 'tags',
    )
    serializer_class = serializers.ApplicationSerializer
    filterset_class = filtersets.ApplicationFilterSet


class ApplicationFlowViewSet(NetBoxModelViewSet):
    queryset = ApplicationFlow.objects.select_related(
        'site', 'source', 'target',
    ).prefetch_related('tags')
    serializer_class = serializers.ApplicationFlowSerializer
    filterset_class = filtersets.ApplicationFlowFilterSet

from dcim.api.serializers import DeviceSerializer, SiteSerializer
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers
from virtualization.api.serializers import VirtualMachineSerializer

from ..models import Application, ApplicationFlow, BusinessDomain, BusinessProcess


class BusinessDomainSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_it_landscape-api:businessdomain-detail',
    )
    site = SiteSerializer(nested=True)

    class Meta:
        model = BusinessDomain
        fields = (
            'id', 'url', 'display', 'site', 'name', 'description', 'color',
            'tags', 'custom_fields', 'created', 'last_updated',
        )
        brief_fields = ('id', 'url', 'display', 'name')


class BusinessProcessSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_it_landscape-api:businessprocess-detail',
    )
    domain = BusinessDomainSerializer(nested=True)

    class Meta:
        model = BusinessProcess
        fields = (
            'id', 'url', 'display', 'domain', 'name', 'description',
            'tags', 'custom_fields', 'created', 'last_updated',
        )
        brief_fields = ('id', 'url', 'display', 'name')


class ApplicationSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_it_landscape-api:application-detail',
    )
    processes = BusinessProcessSerializer(nested=True, many=True, required=False)
    virtual_machines = VirtualMachineSerializer(nested=True, many=True, required=False)
    devices = DeviceSerializer(nested=True, many=True, required=False)
    is_multi_site = serializers.BooleanField(read_only=True)

    class Meta:
        model = Application
        fields = (
            'id', 'url', 'display', 'name', 'processes', 'is_multi_site',
            'description', 'editor', 'referent', 'hosting', 'criticality',
            'monitoring_url',
            'interface_administrative', 'interface_medicale',
            'interface_facturation', 'interface_planification',
            'interface_autre',
            'virtual_machines', 'devices',
            'tags', 'custom_fields', 'created', 'last_updated',
        )
        brief_fields = ('id', 'url', 'display', 'name')


class ApplicationFlowSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_it_landscape-api:applicationflow-detail',
    )
    site = SiteSerializer(nested=True, required=False, allow_null=True)
    source = ApplicationSerializer(nested=True)
    target = ApplicationSerializer(nested=True)

    class Meta:
        model = ApplicationFlow
        fields = (
            'id', 'url', 'display', 'flow_id', 'site', 'source', 'target',
            'protocol', 'port', 'message_type', 'interface_type', 'eai',
            'description', 'tags', 'custom_fields', 'created', 'last_updated',
        )
        brief_fields = ('id', 'url', 'display', 'flow_id')

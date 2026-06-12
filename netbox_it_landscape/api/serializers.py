from rest_framework import serializers

from dcim.api.serializers import DeviceSerializer, SiteSerializer
from netbox.api.serializers import NetBoxModelSerializer
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
    process = BusinessProcessSerializer(nested=True)
    virtual_machines = VirtualMachineSerializer(nested=True, many=True, required=False)
    devices = DeviceSerializer(nested=True, many=True, required=False)

    class Meta:
        model = Application
        fields = (
            'id', 'url', 'display', 'process', 'name', 'trigramme',
            'description', 'editor', 'referent', 'hosting', 'criticality',
            'multi_site', 'monitoring_url',
            'interface_administrative', 'interface_medicale',
            'interface_facturation', 'interface_planification',
            'interface_autre',
            'virtual_machines', 'devices',
            'tags', 'custom_fields', 'created', 'last_updated',
        )
        brief_fields = ('id', 'url', 'display', 'name', 'trigramme')


class ApplicationFlowSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_it_landscape-api:applicationflow-detail',
    )
    source = ApplicationSerializer(nested=True)
    target = ApplicationSerializer(nested=True)

    class Meta:
        model = ApplicationFlow
        fields = (
            'id', 'url', 'display', 'flow_id', 'source', 'target',
            'protocol', 'port', 'message_type', 'interface_type', 'eai',
            'description', 'tags', 'custom_fields', 'created', 'last_updated',
        )
        brief_fields = ('id', 'url', 'display', 'flow_id')

from django import forms
from dcim.models import Device, Site
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm
from utilities.forms.fields import (
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from virtualization.models import VirtualMachine

from .choices import CriticalityChoices, InterfaceTypeChoices
from .models import Application, ApplicationFlow, BusinessDomain, BusinessProcess


#
# Domaines métier
#

class BusinessDomainForm(NetBoxModelForm):
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        label='Établissement',
    )

    class Meta:
        model = BusinessDomain
        fields = ('site', 'name', 'description', 'color', 'tags')


class BusinessDomainFilterForm(NetBoxModelFilterSetForm):
    model = BusinessDomain
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label='Établissement',
    )
    tag = TagFilterField(model)


#
# Processus métier
#

class BusinessProcessForm(NetBoxModelForm):
    domain = DynamicModelChoiceField(
        queryset=BusinessDomain.objects.all(),
        label='Domaine',
    )

    class Meta:
        model = BusinessProcess
        fields = ('domain', 'name', 'description', 'tags')


class BusinessProcessFilterForm(NetBoxModelFilterSetForm):
    model = BusinessProcess
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label='Établissement',
    )
    domain_id = DynamicModelMultipleChoiceField(
        queryset=BusinessDomain.objects.all(),
        required=False,
        label='Domaine',
    )
    tag = TagFilterField(model)


#
# Applications
#

class ApplicationForm(NetBoxModelForm):
    process = DynamicModelChoiceField(
        queryset=BusinessProcess.objects.all(),
        label='Processus',
    )
    virtual_machines = DynamicModelMultipleChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        label='Machines virtuelles',
    )
    devices = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label='Équipements',
    )

    class Meta:
        model = Application
        fields = (
            'process', 'name', 'trigramme', 'description',
            'editor', 'referent', 'hosting', 'criticality', 'multi_site',
            'monitoring_url',
            'interface_administrative', 'interface_medicale',
            'interface_facturation', 'interface_planification',
            'interface_autre',
            'virtual_machines', 'devices', 'tags',
        )


class ApplicationFilterForm(NetBoxModelFilterSetForm):
    model = Application
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label='Établissement',
    )
    domain_id = DynamicModelMultipleChoiceField(
        queryset=BusinessDomain.objects.all(),
        required=False,
        label='Domaine',
    )
    process_id = DynamicModelMultipleChoiceField(
        queryset=BusinessProcess.objects.all(),
        required=False,
        label='Processus',
    )
    criticality = forms.MultipleChoiceField(
        choices=CriticalityChoices,
        required=False,
        label='Criticité',
    )
    trigramme = forms.CharField(required=False, label='Trigramme')
    tag = TagFilterField(model)


#
# Flux applicatifs
#

class ApplicationFlowForm(NetBoxModelForm):
    source = DynamicModelChoiceField(
        queryset=Application.objects.all(),
        label='Application source',
    )
    target = DynamicModelChoiceField(
        queryset=Application.objects.all(),
        label='Application cible',
    )

    class Meta:
        model = ApplicationFlow
        fields = (
            'flow_id', 'source', 'target', 'protocol', 'port',
            'message_type', 'interface_type', 'eai', 'description', 'tags',
        )


class ApplicationFlowFilterForm(NetBoxModelFilterSetForm):
    model = ApplicationFlow
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label='Établissement',
    )
    source_id = DynamicModelMultipleChoiceField(
        queryset=Application.objects.all(),
        required=False,
        label='Application source',
    )
    target_id = DynamicModelMultipleChoiceField(
        queryset=Application.objects.all(),
        required=False,
        label='Application cible',
    )
    interface_type = forms.MultipleChoiceField(
        choices=InterfaceTypeChoices,
        required=False,
        label="Type d'interface",
    )
    protocol = forms.CharField(required=False, label='Protocole')
    eai = forms.CharField(required=False, label='EAI')
    tag = TagFilterField(model)

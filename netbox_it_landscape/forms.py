from dcim.models import Device, Site
from django import forms
from django.utils.translation import gettext_lazy as _
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
# Business domains
#

class BusinessDomainForm(NetBoxModelForm):
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        label=_('Establishment'),
    )

    class Meta:
        model = BusinessDomain
        fields = ('site', 'name', 'description', 'color', 'tags')


class BusinessDomainFilterForm(NetBoxModelFilterSetForm):
    model = BusinessDomain
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label=_('Establishment'),
    )
    tag = TagFilterField(model)


#
# Business processes
#

class BusinessProcessForm(NetBoxModelForm):
    domain = DynamicModelChoiceField(
        queryset=BusinessDomain.objects.all(),
        label=_('Domain'),
    )

    class Meta:
        model = BusinessProcess
        fields = ('domain', 'name', 'description', 'tags')


class BusinessProcessFilterForm(NetBoxModelFilterSetForm):
    model = BusinessProcess
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label=_('Establishment'),
    )
    domain_id = DynamicModelMultipleChoiceField(
        queryset=BusinessDomain.objects.all(),
        required=False,
        label=_('Domain'),
    )
    tag = TagFilterField(model)


#
# Applications
#

class ApplicationForm(NetBoxModelForm):
    processes = DynamicModelMultipleChoiceField(
        queryset=BusinessProcess.objects.all(),
        required=False,
        label=_('Processes'),
        help_text=_(
            'Business attachments — several processes allowed, including in '
            'different facilities (multi-site)'
        ),
    )
    virtual_machines = DynamicModelMultipleChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        label=_('Virtual machines'),
    )
    devices = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label=_('Devices'),
    )

    class Meta:
        model = Application
        fields = (
            'name', 'processes', 'description',
            'editor', 'referent', 'hosting', 'criticality',
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
        label=_('Establishment'),
    )
    domain_id = DynamicModelMultipleChoiceField(
        queryset=BusinessDomain.objects.all(),
        required=False,
        label=_('Domain'),
    )
    process_id = DynamicModelMultipleChoiceField(
        queryset=BusinessProcess.objects.all(),
        required=False,
        label=_('Process'),
    )
    criticality = forms.MultipleChoiceField(
        choices=CriticalityChoices,
        required=False,
        label=_('Criticality'),
    )
    tag = TagFilterField(model)


#
# Setup wizard
#

class SetupWizardForm(forms.Form):
    bundle = forms.ChoiceField(label=_('Modeling bundle'))
    site_name = forms.CharField(
        label=_('Facility / site name'),
        max_length=100,
        help_text=_('An existing site with this name will be reused, otherwise it is created'),
    )
    with_apps = forms.BooleanField(
        required=False, initial=True,
        label=_('Load sample applications'),
    )
    with_infra = forms.BooleanField(
        required=False, initial=True,
        label=_('Load sample infrastructure (VLANs, networks, virtual machines)'),
    )
    with_flows = forms.BooleanField(
        required=False, initial=True,
        label=_('Load sample application flows'),
    )

    def __init__(self, *args, **kwargs):
        from .bundles import BUNDLES
        super().__init__(*args, **kwargs)
        self.fields['bundle'].choices = [
            (key, bundle['label']) for key, bundle in BUNDLES.items()
        ]


#
# Application flows
#

class ApplicationFlowForm(NetBoxModelForm):
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label=_('Establishment'),
    )
    source = DynamicModelChoiceField(
        queryset=Application.objects.all(),
        label=_('Source application'),
    )
    target = DynamicModelChoiceField(
        queryset=Application.objects.all(),
        label=_('Target application'),
    )

    class Meta:
        model = ApplicationFlow
        fields = (
            'flow_id', 'site', 'source', 'target', 'protocol', 'port',
            'message_type', 'interface_type', 'eai', 'description', 'tags',
        )


class ApplicationFlowFilterForm(NetBoxModelFilterSetForm):
    model = ApplicationFlow
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label=_('Establishment'),
    )
    source_id = DynamicModelMultipleChoiceField(
        queryset=Application.objects.all(),
        required=False,
        label=_('Source application'),
    )
    target_id = DynamicModelMultipleChoiceField(
        queryset=Application.objects.all(),
        required=False,
        label=_('Target application'),
    )
    interface_type = forms.MultipleChoiceField(
        choices=InterfaceTypeChoices,
        required=False,
        label=_('Interface type'),
    )
    protocol = forms.CharField(required=False, label=_('Protocol'))
    eai = forms.CharField(required=False, label=_('EAI'))
    tag = TagFilterField(model)

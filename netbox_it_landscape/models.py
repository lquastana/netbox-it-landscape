from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from netbox.models import NetBoxModel
from utilities.fields import ColorField

from .choices import (
    CriticalityChoices,
    InterfaceTypeChoices,
)


class BusinessDomain(NetBoxModel):
    """
    Business domain of a facility (e.g. "Patient administration",
    "Production"). The facility is a NetBox Site.
    """
    site = models.ForeignKey(
        to='dcim.Site',
        on_delete=models.CASCADE,
        related_name='business_domains',
        verbose_name=_('Establishment'),
    )
    name = models.CharField(_('Name'), max_length=100)
    description = models.CharField(_('Description'), max_length=200, blank=True)
    color = ColorField(_('Color'), default='e5f4fd')

    class Meta:
        ordering = ('site', 'name')
        constraints = (
            models.UniqueConstraint(
                fields=('site', 'name'),
                name='%(app_label)s_%(class)s_unique_site_name',
            ),
        )
        verbose_name = _('business domain')
        verbose_name_plural = _('business domains')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('plugins:netbox_it_landscape:businessdomain', args=[self.pk])


class BusinessProcess(NetBoxModel):
    """
    Business process attached to a domain (e.g. "Admissions", "EHR").
    """
    domain = models.ForeignKey(
        to=BusinessDomain,
        on_delete=models.CASCADE,
        related_name='processes',
        verbose_name=_('Domain'),
    )
    name = models.CharField(_('Name'), max_length=100)
    description = models.CharField(_('Description'), max_length=200, blank=True)

    class Meta:
        ordering = ('domain', 'name')
        constraints = (
            models.UniqueConstraint(
                fields=('domain', 'name'),
                name='%(app_label)s_%(class)s_unique_domain_name',
            ),
        )
        verbose_name = _('business process')
        verbose_name_plural = _('business processes')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('plugins:netbox_it_landscape:businessprocess', args=[self.pk])

    @property
    def site(self):
        return self.domain.site


class Application(NetBoxModel):
    """
    IS application. An application is unique in the referential and may be
    attached to several business processes — hence several facilities: the
    multi-site notion is derived from those attachments. Servers (VMs /
    devices) are linked directly.
    """
    processes = models.ManyToManyField(
        to=BusinessProcess,
        related_name='applications',
        blank=True,
        verbose_name=_('Processes'),
    )
    name = models.CharField(_('Name'), max_length=200, unique=True)
    description = models.CharField(_('Description'), max_length=500, blank=True)
    editor = models.CharField(_('Vendor'), max_length=100, blank=True)
    referent = models.CharField(_('Contact person'), max_length=100, blank=True)
    hosting = models.CharField(
        _('Hosting'), max_length=100, blank=True,
        help_text=_('Hosting location (facility, SaaS, …)'),
    )
    criticality = models.CharField(
        _('Criticality'), max_length=30,
        choices=CriticalityChoices,
        default=CriticalityChoices.STANDARD,
    )
    monitoring_url = models.URLField(
        _('Monitoring URL'), blank=True,
        help_text=_('Link to the monitoring tool (PRTG, Centreon, …)'),
    )

    # Active interfaces (flags inherited from the it-landscape model)
    interface_administrative = models.BooleanField(_('Administrative interface'), default=False)
    interface_medicale = models.BooleanField(_('Medical interface'), default=False)
    interface_facturation = models.BooleanField(_('Billing interface'), default=False)
    interface_planification = models.BooleanField(_('Scheduling interface'), default=False)
    interface_autre = models.BooleanField(_('Other interface'), default=False)

    # Direct attachment to the NetBox infrastructure
    virtual_machines = models.ManyToManyField(
        to='virtualization.VirtualMachine',
        related_name='it_landscape_applications',
        blank=True,
        verbose_name=_('Virtual machines'),
    )
    devices = models.ManyToManyField(
        to='dcim.Device',
        related_name='it_landscape_applications',
        blank=True,
        verbose_name=_('Devices'),
    )

    clone_fields = ('editor', 'hosting', 'criticality')

    class Meta:
        ordering = ('name',)
        verbose_name = _('application')
        verbose_name_plural = _('applications')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('plugins:netbox_it_landscape:application', args=[self.pk])

    def get_criticality_color(self):
        return CriticalityChoices.colors.get(self.criticality)

    @property
    def site_list(self):
        """Distinct facilities where the application is deployed (via its processes)."""
        sites = []
        for process in self.processes.all():
            site = process.domain.site
            if site not in sites:
                sites.append(site)
        return sites

    @property
    def is_multi_site(self):
        """Multi-site: derived from the process attachments."""
        return len(self.site_list) > 1

    @property
    def active_interfaces(self):
        labels = []
        if self.interface_administrative:
            labels.append(_('Administrative'))
        if self.interface_medicale:
            labels.append(_('Medical'))
        if self.interface_facturation:
            labels.append(_('Billing'))
        if self.interface_planification:
            labels.append(_('Scheduling'))
        if self.interface_autre:
            labels.append(_('Other'))
        return labels


class ApplicationFlow(NetBoxModel):
    """
    Application flow between two applications: protocol, port, message
    type, interface type and transport EAI.
    """
    flow_id = models.CharField(
        _('Identifier'), max_length=50, blank=True,
        help_text=_('Functional flow identifier (e.g. VDL-FLX-001)'),
    )
    site = models.ForeignKey(
        to='dcim.Site',
        on_delete=models.SET_NULL,
        related_name='application_flows',
        null=True,
        blank=True,
        verbose_name=_('Establishment'),
        help_text=_('Facility where this flow is in place'),
    )
    source = models.ForeignKey(
        to=Application,
        on_delete=models.CASCADE,
        related_name='flows_as_source',
        verbose_name=_('Source application'),
    )
    target = models.ForeignKey(
        to=Application,
        on_delete=models.CASCADE,
        related_name='flows_as_target',
        verbose_name=_('Target application'),
    )
    protocol = models.CharField(_('Protocol'), max_length=50, blank=True)
    port = models.PositiveIntegerField(_('Port'), null=True, blank=True)
    message_type = models.CharField(_('Message type'), max_length=50, blank=True)
    interface_type = models.CharField(
        _('Interface type'), max_length=30,
        choices=InterfaceTypeChoices,
        default=InterfaceTypeChoices.AUTRE,
    )
    eai = models.CharField(
        _('EAI'), max_length=100, blank=True,
        help_text=_('Integration engine carrying the flow (or "Direct")'),
    )
    description = models.CharField(_('Description'), max_length=200, blank=True)

    clone_fields = ('site', 'source', 'target', 'protocol', 'interface_type', 'eai')

    class Meta:
        ordering = ('flow_id', 'source', 'target')
        verbose_name = _('application flow')
        verbose_name_plural = _('application flows')

    def __str__(self):
        label = f'{self.source.name} → {self.target.name}'
        if self.protocol:
            label += f' ({self.protocol})'
        return label

    def get_absolute_url(self):
        return reverse('plugins:netbox_it_landscape:applicationflow', args=[self.pk])

    def get_interface_type_color(self):
        return InterfaceTypeChoices.colors.get(self.interface_type)

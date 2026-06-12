from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel
from utilities.fields import ColorField

from .choices import CriticalityChoices, InterfaceTypeChoices


class BusinessDomain(NetBoxModel):
    """
    Domaine métier d'un établissement (ex. « DP Administrative », « Plateau technique »).
    L'établissement est porté par le Site NetBox.
    """
    site = models.ForeignKey(
        to='dcim.Site',
        on_delete=models.CASCADE,
        related_name='business_domains',
        verbose_name='Établissement',
    )
    name = models.CharField('Nom', max_length=100)
    description = models.CharField('Description', max_length=200, blank=True)
    color = ColorField('Couleur', default='e5f4fd')

    class Meta:
        ordering = ('site', 'name')
        constraints = (
            models.UniqueConstraint(
                fields=('site', 'name'),
                name='%(app_label)s_%(class)s_unique_site_name',
            ),
        )
        verbose_name = 'domaine métier'
        verbose_name_plural = 'domaines métier'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('plugins:netbox_it_landscape:businessdomain', args=[self.pk])


class BusinessProcess(NetBoxModel):
    """
    Processus métier rattaché à un domaine (ex. « GAP », « DPI », « Urgences »).
    """
    domain = models.ForeignKey(
        to=BusinessDomain,
        on_delete=models.CASCADE,
        related_name='processes',
        verbose_name='Domaine',
    )
    name = models.CharField('Nom', max_length=100)
    description = models.CharField('Description', max_length=200, blank=True)

    class Meta:
        ordering = ('domain', 'name')
        constraints = (
            models.UniqueConstraint(
                fields=('domain', 'name'),
                name='%(app_label)s_%(class)s_unique_domain_name',
            ),
        )
        verbose_name = 'processus métier'
        verbose_name_plural = 'processus métier'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('plugins:netbox_it_landscape:businessprocess', args=[self.pk])

    @property
    def site(self):
        return self.domain.site


class Application(NetBoxModel):
    """
    Application du SI. Une application est unique dans le référentiel et
    peut être rattachée à plusieurs processus métier — donc à plusieurs
    établissements : la notion de multi-site est dérivée de ces
    rattachements. Les serveurs (VM / devices) y sont reliés directement.
    """
    processes = models.ManyToManyField(
        to=BusinessProcess,
        related_name='applications',
        blank=True,
        verbose_name='Processus',
    )
    name = models.CharField('Nom', max_length=200, unique=True)
    description = models.CharField('Description', max_length=500, blank=True)
    editor = models.CharField('Éditeur', max_length=100, blank=True)
    referent = models.CharField('Référent', max_length=100, blank=True)
    hosting = models.CharField(
        'Hébergement', max_length=100, blank=True,
        help_text='Lieu d’hébergement (établissement, SaaS, …)',
    )
    criticality = models.CharField(
        'Criticité', max_length=30,
        choices=CriticalityChoices,
        default=CriticalityChoices.STANDARD,
    )
    monitoring_url = models.URLField(
        'URL de supervision', blank=True,
        help_text='Lien vers la supervision (PRTG, Centreon, …)',
    )

    # Interfaces actives (drapeaux repris du modèle it-landscape)
    interface_administrative = models.BooleanField('Interface administrative', default=False)
    interface_medicale = models.BooleanField('Interface médicale', default=False)
    interface_facturation = models.BooleanField('Interface facturation', default=False)
    interface_planification = models.BooleanField('Interface planification', default=False)
    interface_autre = models.BooleanField('Interface autre', default=False)

    # Rattachement direct à l'infrastructure NetBox
    virtual_machines = models.ManyToManyField(
        to='virtualization.VirtualMachine',
        related_name='it_landscape_applications',
        blank=True,
        verbose_name='Machines virtuelles',
    )
    devices = models.ManyToManyField(
        to='dcim.Device',
        related_name='it_landscape_applications',
        blank=True,
        verbose_name='Équipements',
    )

    clone_fields = ('editor', 'hosting', 'criticality')

    class Meta:
        ordering = ('name',)
        verbose_name = 'application'
        verbose_name_plural = 'applications'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('plugins:netbox_it_landscape:application', args=[self.pk])

    def get_criticality_color(self):
        return CriticalityChoices.colors.get(self.criticality)

    @property
    def site_list(self):
        """Établissements distincts où l'application est déployée (via ses processus)."""
        sites = []
        for process in self.processes.all():
            site = process.domain.site
            if site not in sites:
                sites.append(site)
        return sites

    @property
    def is_multi_site(self):
        """Multi-établissement : dérivé des rattachements aux processus."""
        return len(self.site_list) > 1

    @property
    def active_interfaces(self):
        labels = []
        if self.interface_administrative:
            labels.append('Administrative')
        if self.interface_medicale:
            labels.append('Médicale')
        if self.interface_facturation:
            labels.append('Facturation')
        if self.interface_planification:
            labels.append('Planification')
        if self.interface_autre:
            labels.append('Autre')
        return labels


class ApplicationFlow(NetBoxModel):
    """
    Flux applicatif entre deux applications : protocole, port, type de
    message, type d'interface et EAI de transport.
    """
    flow_id = models.CharField(
        'Identifiant', max_length=50, blank=True,
        help_text='Identifiant fonctionnel du flux (ex. VDL-FLX-001)',
    )
    site = models.ForeignKey(
        to='dcim.Site',
        on_delete=models.SET_NULL,
        related_name='application_flows',
        null=True,
        blank=True,
        verbose_name='Établissement',
        help_text="Établissement dans lequel ce flux est en place",
    )
    source = models.ForeignKey(
        to=Application,
        on_delete=models.CASCADE,
        related_name='flows_as_source',
        verbose_name='Application source',
    )
    target = models.ForeignKey(
        to=Application,
        on_delete=models.CASCADE,
        related_name='flows_as_target',
        verbose_name='Application cible',
    )
    protocol = models.CharField('Protocole', max_length=50, blank=True)
    port = models.PositiveIntegerField('Port', null=True, blank=True)
    message_type = models.CharField('Type de message', max_length=50, blank=True)
    interface_type = models.CharField(
        "Type d'interface", max_length=30,
        choices=InterfaceTypeChoices,
        default=InterfaceTypeChoices.AUTRE,
    )
    eai = models.CharField(
        'EAI', max_length=100, blank=True,
        help_text='Moteur d’intégration assurant le transport (ou « Direct »)',
    )
    description = models.CharField('Description', max_length=200, blank=True)

    clone_fields = ('site', 'source', 'target', 'protocol', 'interface_type', 'eai')

    class Meta:
        ordering = ('flow_id', 'source', 'target')
        verbose_name = 'flux applicatif'
        verbose_name_plural = 'flux applicatifs'

    def __str__(self):
        label = f'{self.source.name} → {self.target.name}'
        if self.protocol:
            label += f' ({self.protocol})'
        return label

    def get_absolute_url(self):
        return reverse('plugins:netbox_it_landscape:applicationflow', args=[self.pk])

    def get_interface_type_color(self):
        return InterfaceTypeChoices.colors.get(self.interface_type)

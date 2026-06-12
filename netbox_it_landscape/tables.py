import django_tables2 as tables
from netbox.tables import ChoiceFieldColumn, NetBoxTable, columns

from .models import Application, ApplicationFlow, BusinessDomain, BusinessProcess


class BusinessDomainTable(NetBoxTable):
    name = tables.Column(linkify=True, verbose_name='Nom')
    site = tables.Column(linkify=True, verbose_name='Établissement')
    color = columns.ColorColumn(verbose_name='Couleur')
    process_count = tables.Column(verbose_name='Processus')
    tags = columns.TagColumn(url_name='plugins:netbox_it_landscape:businessdomain_list')

    class Meta(NetBoxTable.Meta):
        model = BusinessDomain
        fields = ('pk', 'id', 'name', 'site', 'description', 'color', 'process_count', 'tags')
        default_columns = ('name', 'site', 'description', 'process_count')


class BusinessProcessTable(NetBoxTable):
    name = tables.Column(linkify=True, verbose_name='Nom')
    domain = tables.Column(linkify=True, verbose_name='Domaine')
    site = tables.Column(
        accessor='domain__site', linkify=True, verbose_name='Établissement',
    )
    application_count = tables.Column(verbose_name='Applications')
    tags = columns.TagColumn(url_name='plugins:netbox_it_landscape:businessprocess_list')

    class Meta(NetBoxTable.Meta):
        model = BusinessProcess
        fields = ('pk', 'id', 'name', 'domain', 'site', 'description', 'application_count', 'tags')
        default_columns = ('name', 'domain', 'site', 'description', 'application_count')


SITE_LIST_TEMPLATE = """
{% for s in record.site_list %}<a href="{{ s.get_absolute_url }}">{{ s }}</a>{% if not forloop.last %}, {% endif %}{% empty %}&mdash;{% endfor %}
"""


class ApplicationTable(NetBoxTable):
    name = tables.Column(linkify=True, verbose_name='Nom')
    processes = tables.ManyToManyColumn(linkify_item=True, verbose_name='Processus')
    sites = tables.TemplateColumn(
        template_code=SITE_LIST_TEMPLATE,
        verbose_name='Établissements',
        orderable=False,
    )
    is_multi_site = columns.BooleanColumn(verbose_name='Multi-site', orderable=False)
    criticality = ChoiceFieldColumn(verbose_name='Criticité')
    tags = columns.TagColumn(url_name='plugins:netbox_it_landscape:application_list')

    class Meta(NetBoxTable.Meta):
        model = Application
        fields = (
            'pk', 'id', 'name', 'processes', 'sites', 'is_multi_site',
            'editor', 'referent', 'hosting', 'criticality', 'tags',
        )
        default_columns = (
            'name', 'sites', 'is_multi_site', 'editor', 'criticality',
        )


class ApplicationFlowTable(NetBoxTable):
    flow_id = tables.Column(linkify=True, verbose_name='Identifiant')
    source = tables.Column(linkify=True, verbose_name='Source')
    target = tables.Column(linkify=True, verbose_name='Cible')
    interface_type = ChoiceFieldColumn(verbose_name="Type d'interface")
    site = tables.Column(linkify=True, verbose_name='Établissement')
    tags = columns.TagColumn(url_name='plugins:netbox_it_landscape:applicationflow_list')

    class Meta(NetBoxTable.Meta):
        model = ApplicationFlow
        fields = (
            'pk', 'id', 'flow_id', 'source', 'target', 'protocol', 'port',
            'message_type', 'interface_type', 'eai', 'description', 'site', 'tags',
        )
        default_columns = (
            'flow_id', 'source', 'target', 'protocol', 'message_type',
            'interface_type', 'eai', 'site',
        )

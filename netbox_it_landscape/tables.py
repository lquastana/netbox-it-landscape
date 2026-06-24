import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from netbox.tables import ChoiceFieldColumn, NetBoxTable, columns

from .models import (
    Application,
    ApplicationFlow,
    BusinessDomain,
    BusinessProcess,
)


class BusinessDomainTable(NetBoxTable):
    name = tables.Column(linkify=True, verbose_name=_('Name'))
    site = tables.Column(linkify=True, verbose_name=_('Establishment'))
    color = columns.ColorColumn(verbose_name=_('Color'))
    process_count = tables.Column(verbose_name=_('Processes'))
    tags = columns.TagColumn(url_name='plugins:netbox_it_landscape:businessdomain_list')

    class Meta(NetBoxTable.Meta):
        model = BusinessDomain
        fields = ('pk', 'id', 'name', 'site', 'description', 'color', 'process_count', 'tags')
        default_columns = ('name', 'site', 'description', 'process_count')


class BusinessProcessTable(NetBoxTable):
    name = tables.Column(linkify=True, verbose_name=_('Name'))
    domain = tables.Column(linkify=True, verbose_name=_('Domain'))
    site = tables.Column(
        accessor='domain__site', linkify=True, verbose_name=_('Establishment'),
    )
    application_count = tables.Column(verbose_name=_('Applications'))
    tags = columns.TagColumn(url_name='plugins:netbox_it_landscape:businessprocess_list')

    class Meta(NetBoxTable.Meta):
        model = BusinessProcess
        fields = ('pk', 'id', 'name', 'domain', 'site', 'description', 'application_count', 'tags')
        default_columns = ('name', 'domain', 'site', 'description', 'application_count')


SITE_LIST_TEMPLATE = """
{% for s in record.site_list %}
  <a href="{{ s.get_absolute_url }}">{{ s }}</a>{% if not forloop.last %}, {% endif %}
{% empty %}
  &mdash;
{% endfor %}
"""

AUTH_MODES_TEMPLATE = """
{% for label in record.get_authentication_modes_display %}
  <span class="badge text-bg-blue">{{ label }}</span>
{% empty %}
  &mdash;
{% endfor %}
"""


class ApplicationTable(NetBoxTable):
    name = tables.Column(linkify=True, verbose_name=_('Name'))
    processes = tables.ManyToManyColumn(linkify_item=True, verbose_name=_('Processes'))
    sites = tables.TemplateColumn(
        template_code=SITE_LIST_TEMPLATE,
        verbose_name=_('Establishments'),
        orderable=False,
    )
    is_multi_site = columns.BooleanColumn(verbose_name=_('Multi-site'), orderable=False)
    criticality = ChoiceFieldColumn(verbose_name=_('Criticality'))
    authentication_primary = ChoiceFieldColumn(verbose_name=_('Primary auth'))
    authentication_modes = tables.TemplateColumn(
        template_code=AUTH_MODES_TEMPLATE,
        verbose_name=_('Auth modes'),
        orderable=False,
    )
    authentication_maintained = columns.BooleanColumn(verbose_name=_('Auth maintained'))
    tags = columns.TagColumn(url_name='plugins:netbox_it_landscape:application_list')

    class Meta(NetBoxTable.Meta):
        model = Application
        fields = (
            'pk', 'id', 'name', 'processes', 'sites', 'is_multi_site',
            'editor', 'referent', 'hosting', 'criticality',
            'authentication_primary', 'authentication_modes',
            'authentication_maintained', 'tags',
        )
        default_columns = (
            'name', 'sites', 'is_multi_site', 'editor', 'criticality',
            'authentication_primary',
        )


class ApplicationFlowTable(NetBoxTable):
    flow_id = tables.Column(linkify=True, verbose_name=_('Identifier'))
    source = tables.Column(linkify=True, verbose_name=_('Source'))
    target = tables.Column(linkify=True, verbose_name=_('Target'))
    interface_type = ChoiceFieldColumn(verbose_name=_('Interface type'))
    site = tables.Column(linkify=True, verbose_name=_('Establishment'))
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

from django.utils.translation import gettext_lazy as _
from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem

cascade_items = (
    PluginMenuItem(
        link='plugins:netbox_it_landscape:cascade_simulator',
        link_text=_('Impact simulator'),
        permissions=['netbox_it_landscape.view_application'],
    ),
)

cartography_items = (
    PluginMenuItem(
        link='plugins:netbox_it_landscape:kpi_landscape',
        link_text=_('KPI summary'),
        permissions=['netbox_it_landscape.view_application'],
    ),
    PluginMenuItem(
        link='plugins:netbox_it_landscape:business_landscape',
        link_text=_('Business view'),
        permissions=['netbox_it_landscape.view_application'],
    ),
    PluginMenuItem(
        link='plugins:netbox_it_landscape:applicative_landscape',
        link_text=_('Application view'),
        permissions=['netbox_it_landscape.view_application'],
    ),
    PluginMenuItem(
        link='plugins:netbox_it_landscape:flux_landscape',
        link_text=_('Flow view'),
        permissions=['netbox_it_landscape.view_applicationflow'],
    ),
    PluginMenuItem(
        link='plugins:netbox_it_landscape:comparison_landscape',
        link_text=_('Facility comparison'),
        permissions=['netbox_it_landscape.view_application'],
    ),
)

referential_items = (
    PluginMenuItem(
        link='plugins:netbox_it_landscape:businessdomain_list',
        link_text=_('Business domains'),
        permissions=['netbox_it_landscape.view_businessdomain'],
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_it_landscape:businessdomain_add',
                title=_('Add'),
                icon_class='mdi mdi-plus-thick',
                permissions=['netbox_it_landscape.add_businessdomain'],
            ),
        ),
    ),
    PluginMenuItem(
        link='plugins:netbox_it_landscape:businessprocess_list',
        link_text=_('Business processes'),
        permissions=['netbox_it_landscape.view_businessprocess'],
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_it_landscape:businessprocess_add',
                title=_('Add'),
                icon_class='mdi mdi-plus-thick',
                permissions=['netbox_it_landscape.add_businessprocess'],
            ),
        ),
    ),
    PluginMenuItem(
        link='plugins:netbox_it_landscape:application_list',
        link_text=_('Applications'),
        permissions=['netbox_it_landscape.view_application'],
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_it_landscape:application_add',
                title=_('Add'),
                icon_class='mdi mdi-plus-thick',
                permissions=['netbox_it_landscape.add_application'],
            ),
        ),
    ),
    PluginMenuItem(
        link='plugins:netbox_it_landscape:applicationflow_list',
        link_text=_('Application flows'),
        permissions=['netbox_it_landscape.view_applicationflow'],
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_it_landscape:applicationflow_add',
                title=_('Add'),
                icon_class='mdi mdi-plus-thick',
                permissions=['netbox_it_landscape.add_applicationflow'],
            ),
        ),
    ),
)

setup_items = (
    PluginMenuItem(
        link='plugins:netbox_it_landscape:setup_wizard',
        link_text=_('Setup wizard'),
        permissions=['netbox_it_landscape.add_businessdomain'],
    ),
)

menu = PluginMenu(
    label='IT Landscape',
    groups=(
        (_('Cartography'), cartography_items),
        (_('Referential'), referential_items),
        (_('Cascade Impact'), cascade_items),
        (_('Administration'), setup_items),
    ),
    icon_class='mdi mdi-sitemap',
)

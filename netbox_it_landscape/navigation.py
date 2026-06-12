from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem

cartography_items = (
    PluginMenuItem(
        link='plugins:netbox_it_landscape:business_landscape',
        link_text='Vue métier',
        permissions=['netbox_it_landscape.view_application'],
    ),
    PluginMenuItem(
        link='plugins:netbox_it_landscape:applicative_landscape',
        link_text='Vue applicative',
        permissions=['netbox_it_landscape.view_application'],
    ),
    PluginMenuItem(
        link='plugins:netbox_it_landscape:flux_landscape',
        link_text='Vue flux',
        permissions=['netbox_it_landscape.view_applicationflow'],
    ),
)

referential_items = (
    PluginMenuItem(
        link='plugins:netbox_it_landscape:businessdomain_list',
        link_text='Domaines métier',
        permissions=['netbox_it_landscape.view_businessdomain'],
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_it_landscape:businessdomain_add',
                title='Ajouter',
                icon_class='mdi mdi-plus-thick',
                permissions=['netbox_it_landscape.add_businessdomain'],
            ),
        ),
    ),
    PluginMenuItem(
        link='plugins:netbox_it_landscape:businessprocess_list',
        link_text='Processus métier',
        permissions=['netbox_it_landscape.view_businessprocess'],
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_it_landscape:businessprocess_add',
                title='Ajouter',
                icon_class='mdi mdi-plus-thick',
                permissions=['netbox_it_landscape.add_businessprocess'],
            ),
        ),
    ),
    PluginMenuItem(
        link='plugins:netbox_it_landscape:application_list',
        link_text='Applications',
        permissions=['netbox_it_landscape.view_application'],
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_it_landscape:application_add',
                title='Ajouter',
                icon_class='mdi mdi-plus-thick',
                permissions=['netbox_it_landscape.add_application'],
            ),
        ),
    ),
    PluginMenuItem(
        link='plugins:netbox_it_landscape:applicationflow_list',
        link_text='Flux applicatifs',
        permissions=['netbox_it_landscape.view_applicationflow'],
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_it_landscape:applicationflow_add',
                title='Ajouter',
                icon_class='mdi mdi-plus-thick',
                permissions=['netbox_it_landscape.add_applicationflow'],
            ),
        ),
    ),
)

menu = PluginMenu(
    label='IT Landscape',
    groups=(
        ('Cartographie', cartography_items),
        ('Référentiel', referential_items),
    ),
    icon_class='mdi mdi-sitemap',
)

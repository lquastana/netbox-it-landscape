from netbox.plugins import PluginConfig


class ITLandscapeConfig(PluginConfig):
    name = 'netbox_it_landscape'
    verbose_name = 'IT Landscape'
    description = (
        "Cartographie applicative hospitalière intégrée à NetBox : "
        "vues métier, applicative et flux."
    )
    version = '0.4.0'
    author = 'Laurent Quastana'
    base_url = 'it-landscape'
    min_version = '4.0'


config = ITLandscapeConfig

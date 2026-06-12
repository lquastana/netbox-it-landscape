from utilities.choices import ChoiceSet


class CriticalityChoices(ChoiceSet):
    key = 'Application.criticality'

    CRITICAL = 'critical'
    STANDARD = 'standard'

    CHOICES = [
        (CRITICAL, 'Critique', 'red'),
        (STANDARD, 'Standard', 'gray'),
    ]


class InterfaceTypeChoices(ChoiceSet):
    key = 'ApplicationFlow.interface_type'

    ADMINISTRATIVE = 'administrative'
    MEDICALE = 'medicale'
    FACTURATION = 'facturation'
    PLANIFICATION = 'planification'
    AUTRE = 'autre'

    CHOICES = [
        (ADMINISTRATIVE, 'Administrative', 'yellow'),
        (MEDICALE, 'Médicale', 'green'),
        (FACTURATION, 'Facturation', 'red'),
        (PLANIFICATION, 'Planification', 'blue'),
        (AUTRE, 'Autre', 'gray'),
    ]


# Couleurs hexadécimales des types d'interface, reprises de l'application
# it-landscape d'origine (lib/constants.js) pour les vues cartographiques.
INTERFACE_HEX_COLORS = {
    InterfaceTypeChoices.MEDICALE: '#4caf50',
    InterfaceTypeChoices.ADMINISTRATIVE: '#d4b106',
    InterfaceTypeChoices.PLANIFICATION: '#2196f3',
    InterfaceTypeChoices.FACTURATION: '#f44336',
    InterfaceTypeChoices.AUTRE: '#9e9e9e',
}

# Palette des tuiles de domaines (DOMAIN_COLORS de l'app d'origine),
# stockée sans le '#' (format ColorField NetBox).
DOMAIN_COLOR_PALETTE = [
    'e5f4fd',  # bleu très pâle
    'fbf4e9',  # orangé
    'eaf7eb',  # vert
    'f9ebf2',  # rose
    'ede8fd',  # violet
    'fdf3e5',  # beige
]

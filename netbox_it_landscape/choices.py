from django.utils.translation import gettext_lazy as _
from utilities.choices import ChoiceSet


class CriticalityChoices(ChoiceSet):
    key = 'Application.criticality'

    CRITICAL = 'critical'
    STANDARD = 'standard'

    CHOICES = [
        (CRITICAL, _('Critical'), 'red'),
        (STANDARD, _('Standard'), 'gray'),
    ]


class AuthenticationModeChoices(ChoiceSet):
    """
    Authentication modes available for a digital health service
    (digital health security indicator PROC-09A — HospiConnect / HOP'EN 2).
    """
    key = 'Application.authentication_mode'

    LOCAL = 'local'                       # local authentication (account owned by the service)
    IDP_LOCAL = 'idp_local'               # delegation to a local IdP (AD/LDAP, internal SSO)
    PSC = 'pro_sante_connect'             # Pro Santé Connect (e-CPS, sectoral health IdP)
    HOSPICONNECT = 'hospiconnect'         # unified HospiConnect banner
    NONE = 'none'                         # no authentication

    CHOICES = [
        (LOCAL, _('Local authentication'), 'gray'),
        (IDP_LOCAL, _('Local IdP delegation'), 'blue'),
        (PSC, _('Pro Santé Connect'), 'green'),
        (HOSPICONNECT, _('HospiConnect banner'), 'teal'),
        (NONE, _('None'), 'red'),
    ]


class InterfaceTypeChoices(ChoiceSet):
    key = 'ApplicationFlow.interface_type'

    ADMINISTRATIVE = 'administrative'
    MEDICALE = 'medicale'
    FACTURATION = 'facturation'
    PLANIFICATION = 'planification'
    AUTRE = 'autre'

    CHOICES = [
        (ADMINISTRATIVE, _('Administrative'), 'yellow'),
        (MEDICALE, _('Medical'), 'green'),
        (FACTURATION, _('Billing'), 'red'),
        (PLANIFICATION, _('Scheduling'), 'blue'),
        (AUTRE, _('Other'), 'gray'),
    ]


# Hex colors for interface types, inherited from the original it-landscape
# application (lib/constants.js), used in the landscape views.
INTERFACE_HEX_COLORS = {
    InterfaceTypeChoices.MEDICALE: '#4caf50',
    InterfaceTypeChoices.ADMINISTRATIVE: '#d4b106',
    InterfaceTypeChoices.PLANIFICATION: '#2196f3',
    InterfaceTypeChoices.FACTURATION: '#f44336',
    InterfaceTypeChoices.AUTRE: '#9e9e9e',
}

# Domain tile palette (DOMAIN_COLORS from the original app),
# stored without '#' (NetBox ColorField format).
DOMAIN_COLOR_PALETTE = [
    'e5f4fd',  # pale blue
    'fbf4e9',  # orange
    'eaf7eb',  # green
    'f9ebf2',  # pink
    'ede8fd',  # purple
    'fdf3e5',  # beige
]

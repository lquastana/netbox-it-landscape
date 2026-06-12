from dcim.models import Site
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.views.generic import View

from ..choices import INTERFACE_HEX_COLORS, InterfaceTypeChoices


class BaseLandscapeView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """
    Base for landscape views: anonymous users are redirected to the login
    page, authenticated users without the required permission get a 403
    (Django's AccessMixin default behaviour).
    """


def interface_chips(app):
    """Build the interface chips (label + colors) of an application."""
    mapping = [
        ('interface_administrative', _('Administrative'), InterfaceTypeChoices.ADMINISTRATIVE),
        ('interface_medicale', _('Medical'), InterfaceTypeChoices.MEDICALE),
        ('interface_facturation', _('Billing'), InterfaceTypeChoices.FACTURATION),
        ('interface_planification', _('Scheduling'), InterfaceTypeChoices.PLANIFICATION),
        ('interface_autre', _('Other'), InterfaceTypeChoices.AUTRE),
    ]
    chips = []
    for field, label, key in mapping:
        if getattr(app, field):
            color = INTERFACE_HEX_COLORS[key]
            chips.append({'label': label, 'color': color, 'bg': f'{color}22'})
    return chips


def landscape_filters(request):
    """Common GET filters of the landscape views."""
    site_id = request.GET.get('site_id') or ''
    q = (request.GET.get('q') or '').strip()
    criticality = request.GET.get('criticality') or ''
    sites = Site.objects.filter(business_domains__isnull=False).distinct().order_by('name')
    return site_id, q, criticality, sites

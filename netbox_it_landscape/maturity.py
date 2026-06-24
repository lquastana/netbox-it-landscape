"""
Digital health security maturity helpers.

Currently exposes the PROC-09A indicator (HospiConnect / HOP'EN 2):
maturity of the cartography of authentication modes available per digital
health service. The level (0→4) is derived from the share of applications
with a documented authentication mapping and a maintenance rule.
"""
from django.db.models import Q


def proc09a_level(applications):
    """
    Return (level, stats) for the PROC-09A indicator over a queryset of
    Application objects.

    Levels (indicative thresholds, aligned with the indicator scale):
      0 — no authentication cartography
      1 — informal/partial (documented for < 50% of services)
      2 — formalized for part of the services
      3 — applicable/exploitable for the majority, with maintenance rules
      4 — stabilized for the whole scope, homogeneously
    """
    total = applications.count()
    if not total:
        return 0, {'total': 0, 'documented': 0, 'maintained': 0,
                   'coverage_pct': 0, 'maintained_pct': 0}

    documented_qs = applications.filter(Q(authentication_modes__len__gt=0))
    maintained_qs = documented_qs.filter(authentication_maintained=True)
    documented = documented_qs.count()
    maintained = maintained_qs.count()

    cov = documented / total
    cov_maint = maintained / total

    if cov == 0:
        level = 0
    elif cov < 0.5:
        level = 1
    elif cov_maint < 0.75:
        level = 2
    elif cov_maint < 0.95:
        level = 3
    else:
        level = 4

    return level, {
        'total': total,
        'documented': documented,
        'maintained': maintained,
        'coverage_pct': round(100 * cov),
        'maintained_pct': round(100 * cov_maint),
    }

from dcim.models import Site
from django.shortcuts import render
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from extras.models import JournalEntry

from ..bundles import BUNDLES
from ..forms import SetupWizardForm
from ..seeding import apply_bundle
from .base import BaseLandscapeView


class SetupWizardView(BaseLandscapeView):
    """Setup wizard: apply a sector modeling bundle to a (new or existing) site."""
    template_name = 'netbox_it_landscape/landscape/wizard.html'
    permission_required = (
        'netbox_it_landscape.add_businessdomain',
        'netbox_it_landscape.add_businessprocess',
    )

    # Permissions required by each optional seeding step. The wizard creates
    # objects outside the plugin (dcim / ipam / virtualization / extras), so
    # the user must hold those rights explicitly — no privilege escalation.
    INFRA_PERMS = (
        'virtualization.add_virtualmachine',
        'virtualization.add_vminterface',
        'ipam.add_vlan',
        'ipam.add_prefix',
        'ipam.add_ipaddress',
        'extras.add_tag',
    )

    def _option_permissions(self, user):
        return {
            'with_apps': user.has_perm('netbox_it_landscape.add_application'),
            'with_flows': user.has_perm('netbox_it_landscape.add_applicationflow'),
            'with_infra': all(user.has_perm(perm) for perm in self.INFRA_PERMS),
            'create_site': user.has_perm('dcim.add_site'),
        }

    def _bundle_cards(self):
        return [
            {
                'key': key,
                'label': bundle['label'],
                'description': bundle['description'],
                'icon': bundle.get('icon', 'mdi-sitemap'),
                'domain_count': len(bundle['domains']),
                'process_count': sum(len(d['processes']) for d in bundle['domains']),
                'app_count': len(bundle['applications']),
                'vm_count': len(bundle.get('vms', [])),
                'vlan_count': len(bundle.get('vlans', [])),
                'flow_count': len(bundle.get('flows', [])),
            }
            for key, bundle in BUNDLES.items()
        ]

    def get(self, request):
        return render(request, self.template_name, {
            'form': SetupWizardForm(),
            'bundles': self._bundle_cards(),
            'option_perms': self._option_permissions(request.user),
        })

    def post(self, request):
        option_perms = self._option_permissions(request.user)
        form = SetupWizardForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {
                'form': form,
                'bundles': self._bundle_cards(),
                'option_perms': option_perms,
            })

        bundle = BUNDLES[form.cleaned_data['bundle']]
        site_name = form.cleaned_data['site_name'].strip()
        site = Site.objects.filter(name__iexact=site_name).first()

        # Server-side enforcement of per-option permissions
        permission_errors = []
        if form.cleaned_data['with_apps'] and not option_perms['with_apps']:
            permission_errors.append(_('You do not have permission to create applications.'))
        if form.cleaned_data['with_flows'] and not option_perms['with_flows']:
            permission_errors.append(_('You do not have permission to create application flows.'))
        if form.cleaned_data['with_infra'] and not option_perms['with_infra']:
            permission_errors.append(_(
                'You do not have permission to create the sample infrastructure '
                '(virtual machines, VLANs, prefixes, IP addresses, tags).'
            ))
        if not site and not option_perms['create_site']:
            permission_errors.append(_(
                'This site does not exist and you do not have permission to create sites.'
            ))
        if permission_errors:
            return render(request, self.template_name, {
                'form': form,
                'bundles': self._bundle_cards(),
                'option_perms': option_perms,
                'permission_errors': permission_errors,
            }, status=403)

        site_created = False
        if not site:
            site = Site.objects.create(
                name=site_name,
                slug=slugify(site_name)[:100],
                status='active',
            )
            site_created = True

        stats = apply_bundle(
            site, bundle,
            with_apps=form.cleaned_data['with_apps'],
            with_infra=form.cleaned_data['with_infra'],
            with_flows=form.cleaned_data['with_flows'],
        )

        # Traceability: record the seeding in the site's journal
        JournalEntry.objects.create(
            assigned_object=site,
            created_by=request.user,
            kind='info',
            comments=(
                f"IT Landscape setup wizard — bundle '{bundle['label']}': "
                f"{stats['domains']} domains, {stats['processes']} processes, "
                f"{stats['applications']} applications, {stats['flows']} flows, "
                f"{stats['vms']} VMs, {stats['vlans']} VLANs, "
                f"{stats['prefixes']} prefixes created."
            ),
        )

        return render(request, self.template_name, {
            'form': SetupWizardForm(),
            'bundles': self._bundle_cards(),
            'option_perms': option_perms,
            'result': {
                'site': site,
                'site_created': site_created,
                'bundle_label': bundle['label'],
                'stats': stats,
            },
        })

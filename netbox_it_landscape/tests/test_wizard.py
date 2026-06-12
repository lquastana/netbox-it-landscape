"""
Setup wizard tests: bundle application, idempotence, and per-option
permission enforcement (no privilege escalation to dcim/ipam objects).
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from dcim.models import Site
from ipam.models import VLAN
from virtualization.models import VirtualMachine

from netbox_it_landscape.models import (
    Application,
    ApplicationFlow,
    BusinessDomain,
    BusinessProcess,
)

from .utils import grant_permission

User = get_user_model()

WIZARD_URL = 'plugins:netbox_it_landscape:setup_wizard'


def wizard_payload(**overrides):
    payload = {
        'bundle': 'sih',
        'site_name': 'CH Test',
        'with_apps': 'on',
        'with_infra': 'on',
        'with_flows': 'on',
    }
    payload.update(overrides)
    return {k: v for k, v in payload.items() if v is not None}


class SetupWizardTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.superuser = User.objects.create_superuser(username='root', password='secret')

    def _counts(self):
        return {
            'domains': BusinessDomain.objects.count(),
            'processes': BusinessProcess.objects.count(),
            'applications': Application.objects.count(),
            'flows': ApplicationFlow.objects.count(),
            'vms': VirtualMachine.objects.count(),
            'vlans': VLAN.objects.count(),
        }

    def test_apply_sih_bundle_creates_objects(self):
        self.client.force_login(self.superuser)
        response = self.client.post(reverse(WIZARD_URL), wizard_payload())
        self.assertEqual(response.status_code, 200)

        site = Site.objects.filter(name='CH Test').first()
        self.assertIsNotNone(site)
        counts = self._counts()
        self.assertGreater(counts['domains'], 0)
        self.assertGreater(counts['applications'], 0)
        self.assertGreater(counts['flows'], 0)
        self.assertGreater(counts['vms'], 0)
        self.assertGreater(counts['vlans'], 0)
        # Sample VMs get a primary IP
        self.assertTrue(
            VirtualMachine.objects.filter(primary_ip4__isnull=False).exists()
        )

    def test_bundle_application_is_idempotent(self):
        self.client.force_login(self.superuser)
        self.client.post(reverse(WIZARD_URL), wizard_payload())
        first = self._counts()
        self.client.post(reverse(WIZARD_URL), wizard_payload())
        self.assertEqual(first, self._counts())

    def test_structure_only_when_options_disabled(self):
        self.client.force_login(self.superuser)
        response = self.client.post(reverse(WIZARD_URL), wizard_payload(
            with_apps=None, with_infra=None, with_flows=None,
        ))
        self.assertEqual(response.status_code, 200)
        self.assertGreater(BusinessDomain.objects.count(), 0)
        self.assertEqual(Application.objects.count(), 0)
        self.assertEqual(VirtualMachine.objects.count(), 0)

    def test_infra_option_requires_dcim_permissions(self):
        """A user with plugin-only rights must not create VMs/VLANs via the wizard."""
        user = User.objects.create_user(username='plugin-admin', password='secret')
        for model in (BusinessDomain, BusinessProcess, Application, ApplicationFlow):
            grant_permission(user, model, 'add', 'view')
        site = Site.objects.create(name='CH Existant', slug='ch-existant', status='active')

        self.client.force_login(user)
        response = self.client.post(reverse(WIZARD_URL), wizard_payload(site_name=site.name))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(VirtualMachine.objects.count(), 0)
        self.assertEqual(VLAN.objects.count(), 0)

    def test_site_creation_requires_dcim_add_site(self):
        user = User.objects.create_user(username='plugin-admin2', password='secret')
        for model in (BusinessDomain, BusinessProcess, Application, ApplicationFlow):
            grant_permission(user, model, 'add', 'view')

        self.client.force_login(user)
        response = self.client.post(reverse(WIZARD_URL), wizard_payload(
            site_name='Site Inexistant', with_infra=None,
        ))
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Site.objects.filter(name='Site Inexistant').exists())

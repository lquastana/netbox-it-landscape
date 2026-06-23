"""
Tests for the cascade impact simulator: permission gating, the empty
(no-scenario) page, and the BFS propagation through application flows.
"""
from dcim.models import Site
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from netbox_it_landscape.models import (
    Application,
    ApplicationFlow,
    BusinessDomain,
    BusinessProcess,
)

from .utils import grant_permission

User = get_user_model()

CASCADE_URL = 'plugins:netbox_it_landscape:cascade_simulator'


class CascadeSimulatorPermissionTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_no_perm = User.objects.create_user(username='noperm', password='secret')
        cls.user_viewer = User.objects.create_user(username='viewer', password='secret')
        grant_permission(cls.user_viewer, Application, 'view')

    def test_anonymous_is_redirected_to_login(self):
        response = self.client.get(reverse(CASCADE_URL))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response['Location'])

    def test_authenticated_without_permission_gets_403(self):
        self.client.force_login(self.user_no_perm)
        response = self.client.get(reverse(CASCADE_URL))
        self.assertEqual(response.status_code, 403)

    def test_viewer_can_access(self):
        self.client.force_login(self.user_viewer)
        response = self.client.get(reverse(CASCADE_URL))
        self.assertEqual(response.status_code, 200)
        # No scenario submitted: no analysis is produced.
        self.assertIsNone(response.context['analysis'])


class CascadeSimulatorAnalysisTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        site = Site.objects.create(name='CH Alpha', slug='ch-alpha')
        domain = BusinessDomain.objects.create(site=site, name='Care')
        cls.process_src = BusinessProcess.objects.create(domain=domain, name='Admissions')
        cls.process_tgt = BusinessProcess.objects.create(domain=domain, name='EHR')

        cls.app_src = Application.objects.create(name='Source app')
        cls.app_tgt = Application.objects.create(name='Target app')
        cls.app_src.processes.add(cls.process_src)
        cls.app_tgt.processes.add(cls.process_tgt)

        cls.flow = ApplicationFlow.objects.create(
            source=cls.app_src,
            target=cls.app_tgt,
            site=site,
        )

        cls.user = User.objects.create_user(username='viewer', password='secret')
        grant_permission(cls.user, Application, 'view')

    def setUp(self):
        self.client.force_login(self.user)

    def _simulate(self, **params):
        return self.client.get(reverse(CASCADE_URL), params)

    def test_failed_application_propagates_to_downstream_target(self):
        response = self._simulate(
            comp_type='application',
            comp_id=str(self.app_src.pk),
            comp_status='hs',
            comp_label=self.app_src.name,
        )
        self.assertEqual(response.status_code, 200)
        analysis = response.context['analysis']
        self.assertIsNotNone(analysis)

        statuses = {row['app'].pk: row['status'] for row in analysis['impacted_apps']}
        # The failed application is down; the downstream target is attenuated.
        self.assertEqual(statuses[self.app_src.pk], 'hs')
        self.assertEqual(statuses[self.app_tgt.pk], 'latence')

        # Both applications and both processes are reported.
        self.assertEqual(analysis['total_apps'], 2)
        self.assertEqual(analysis['total_processes'], 2)

        # The flow touching the severely impacted source is flagged as blocked.
        self.assertEqual(analysis['total_flows'], 1)
        self.assertIn(self.flow, analysis['blocked_flows'])

    def test_failed_application_carries_recommended_actions(self):
        response = self._simulate(
            comp_type='application',
            comp_id=str(self.app_src.pk),
            comp_status='hs',
            comp_label=self.app_src.name,
        )
        src_row = next(
            row for row in response.context['analysis']['impacted_apps']
            if row['app'].pk == self.app_src.pk
        )
        self.assertTrue(src_row['actions'])

    def test_invalid_component_id_is_ignored(self):
        response = self._simulate(
            comp_type='application',
            comp_id='not-a-number',
            comp_status='hs',
            comp_label='bogus',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['analysis']['total_apps'], 0)

"""
Smoke tests: every landscape view must redirect anonymous users to the
login page, return 403 to authenticated users without permission, and 200
to users holding the right view permissions.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from netbox_it_landscape.models import Application, ApplicationFlow

from .utils import grant_permission

User = get_user_model()

LANDSCAPE_URLS = (
    'plugins:netbox_it_landscape:business_landscape',
    'plugins:netbox_it_landscape:applicative_landscape',
    'plugins:netbox_it_landscape:flux_landscape',
    'plugins:netbox_it_landscape:kpi_landscape',
    'plugins:netbox_it_landscape:comparison_landscape',
)


class LandscapeViewPermissionTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_no_perm = User.objects.create_user(username='noperm', password='secret')
        cls.user_viewer = User.objects.create_user(username='viewer', password='secret')
        grant_permission(cls.user_viewer, Application, 'view')
        grant_permission(cls.user_viewer, ApplicationFlow, 'view')

    def test_anonymous_is_redirected_to_login(self):
        for name in LANDSCAPE_URLS + ('plugins:netbox_it_landscape:setup_wizard',):
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 302, name)
            self.assertIn('/login/', response['Location'], name)

    def test_authenticated_without_permission_gets_403(self):
        self.client.force_login(self.user_no_perm)
        for name in LANDSCAPE_URLS + ('plugins:netbox_it_landscape:setup_wizard',):
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 403, name)

    def test_viewer_can_access_landscape_views(self):
        self.client.force_login(self.user_viewer)
        for name in LANDSCAPE_URLS:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200, name)

    def test_viewer_cannot_access_wizard(self):
        self.client.force_login(self.user_viewer)
        response = self.client.get(reverse('plugins:netbox_it_landscape:setup_wizard'))
        self.assertEqual(response.status_code, 403)

    def test_superuser_can_access_everything(self):
        superuser = User.objects.create_superuser(username='root', password='secret')
        self.client.force_login(superuser)
        for name in LANDSCAPE_URLS + ('plugins:netbox_it_landscape:setup_wizard',):
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200, name)

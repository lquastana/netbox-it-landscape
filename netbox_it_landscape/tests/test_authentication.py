"""
Tests for the authentication modes mapping on applications (indicator
PROC-09A): model multi-valued field, filterset, serializer round-trip and
the maturity level computation.
"""
from django.test import TestCase

from netbox_it_landscape.api.serializers import ApplicationSerializer
from netbox_it_landscape.choices import AuthenticationModeChoices
from netbox_it_landscape.filtersets import ApplicationFilterSet
from netbox_it_landscape.maturity import proc09a_level
from netbox_it_landscape.models import Application

PSC = AuthenticationModeChoices.PSC
IDP = AuthenticationModeChoices.IDP_LOCAL
LOCAL = AuthenticationModeChoices.LOCAL


class AuthenticationModelTests(TestCase):

    def test_modes_are_stored_as_list(self):
        app = Application.objects.create(
            name='DPI', authentication_modes=[IDP, PSC],
            authentication_primary=PSC, authentication_maintained=True,
        )
        app.refresh_from_db()
        self.assertEqual(app.authentication_modes, [IDP, PSC])
        self.assertTrue(app.authentication_documented)

    def test_display_helpers(self):
        app = Application.objects.create(
            name='Mailiz', authentication_modes=[PSC], authentication_primary=PSC,
        )
        self.assertEqual(app.get_authentication_modes_display(), ['Pro Santé Connect'])
        self.assertEqual(app.get_authentication_primary_color(), 'green')

    def test_undocumented_application(self):
        app = Application.objects.create(name='WordPress')
        self.assertFalse(app.authentication_documented)
        self.assertEqual(app.get_authentication_modes_display(), [])


class AuthenticationFilterSetTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        Application.objects.create(name='A', authentication_modes=[IDP, PSC])
        Application.objects.create(name='B', authentication_modes=[LOCAL])
        Application.objects.create(name='C')  # undocumented

    def test_filter_by_mode_is_contains_any(self):
        qs = ApplicationFilterSet({'authentication_modes': [PSC]}, Application.objects.all()).qs
        self.assertEqual(set(qs.values_list('name', flat=True)), {'A'})

    def test_filter_documented(self):
        qs = ApplicationFilterSet({'authentication_documented': True}, Application.objects.all()).qs
        self.assertEqual(set(qs.values_list('name', flat=True)), {'A', 'B'})
        qs = ApplicationFilterSet({'authentication_documented': False}, Application.objects.all()).qs
        self.assertEqual(set(qs.values_list('name', flat=True)), {'C'})


class AuthenticationSerializerTests(TestCase):

    def test_round_trip(self):
        serializer = ApplicationSerializer(data={
            'name': 'OncoSuite',
            'authentication_modes': [IDP, PSC],
            'authentication_primary': PSC,
            'authentication_maintained': True,
            'authentication_notes': 'e-CPS via PSC',
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)
        app = serializer.save()
        self.assertEqual(app.authentication_modes, [IDP, PSC])
        self.assertEqual(app.authentication_primary, PSC)
        self.assertTrue(app.authentication_maintained)


class Proc09aMaturityTests(TestCase):

    def test_empty_scope_is_level_zero(self):
        level, stats = proc09a_level(Application.objects.all())
        self.assertEqual(level, 0)
        self.assertEqual(stats['total'], 0)

    def test_partial_coverage_levels(self):
        # 1 documented + maintained out of 4 → coverage 25% → level 1
        Application.objects.create(name='A', authentication_modes=[PSC], authentication_maintained=True)
        Application.objects.create(name='B')
        Application.objects.create(name='C')
        Application.objects.create(name='D')
        level, stats = proc09a_level(Application.objects.all())
        self.assertEqual(stats['documented'], 1)
        self.assertEqual(stats['coverage_pct'], 25)
        self.assertEqual(level, 1)

    def test_full_maintained_coverage_is_level_four(self):
        for name in ('A', 'B', 'C'):
            Application.objects.create(
                name=name, authentication_modes=[IDP], authentication_maintained=True,
            )
        level, stats = proc09a_level(Application.objects.all())
        self.assertEqual(stats['maintained_pct'], 100)
        self.assertEqual(level, 4)

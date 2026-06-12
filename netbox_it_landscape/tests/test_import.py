"""
Tests for the import_it_landscape management command: object creation,
application unification (multi-site) and idempotence.
"""
import json
import tempfile
from pathlib import Path

from dcim.models import Site
from django.core.management import call_command
from django.test import TestCase
from virtualization.models import VirtualMachine

from netbox_it_landscape.models import (
    Application,
    ApplicationFlow,
    BusinessDomain,
    BusinessProcess,
)

METIER = {
    'etablissements': [{
        'nom': 'CH Alpha',
        'domaines': [{
            'nom': 'Gestion',
            'description': 'Domaine de gestion',
            'processus': [{
                'nom': 'Facturation',
                'description': 'Processus de facturation',
                'applications': [
                    {
                        'nom': 'AppFact',
                        'trigramme': 'FAC',
                        'description': 'Facturation des séjours',
                        'editeur': 'ACME',
                        'criticite': 'Critique',
                        'interfaces': {'Facturation': True, 'Administrative': True},
                    },
                    {
                        'nom': 'AppCompta',
                        'trigramme': 'CPT',
                        'criticite': 'Standard',
                        'interfaces': {},
                    },
                ],
            }],
        }],
    }],
}

METIER_B = {
    'etablissements': [{
        'nom': 'CH Beta',
        'domaines': [{
            'nom': 'Gestion',
            'processus': [{
                'nom': 'Facturation',
                'applications': [
                    # Same application deployed on a second facility → multi-site
                    {'nom': 'AppFact', 'trigramme': 'FAC', 'criticite': 'Critique', 'interfaces': {}},
                ],
            }],
        }],
    }],
}

FLUX = {
    'etablissement': 'CH Alpha',
    'flux': [{
        'id': 'ALP-FLX-001',
        'sourceTrigramme': 'FAC',
        'targetTrigramme': 'CPT',
        'protocol': 'SFTP',
        'port': 22,
        'messageType': 'Factures',
        'interfaceType': 'Facturation',
        'eaiName': 'ETL',
        'description': 'Export comptable',
    }],
}

INFRA = {
    'etablissement': 'CH Alpha',
    'serveurs': [{
        'VM': 'alpha-fact-01',
        'PrimaryIPAddress': '10.99.10.10',
        'RoleServeur': 'Serveur facturation',
        'CPUs': 2,
        'MemoryMiB': 4096,
        'TotalDiskCapacityMiB': 51200,
        'trigramme': 'FAC',
    }],
}

TRIGRAMMES = {'FAC': 'AppFact', 'CPT': 'AppCompta'}


class ImportCommandTests(TestCase):

    def _write_dataset(self, directory):
        directory = Path(directory)
        (directory / 'ch_alpha.json').write_text(json.dumps(METIER), encoding='utf-8')
        (directory / 'ch_alpha.flux.json').write_text(json.dumps(FLUX), encoding='utf-8')
        (directory / 'ch_alpha.infra.json').write_text(json.dumps(INFRA), encoding='utf-8')
        (directory / 'ch_beta.json').write_text(json.dumps(METIER_B), encoding='utf-8')
        (directory / 'trigrammes.json').write_text(json.dumps(TRIGRAMMES), encoding='utf-8')

    def _counts(self):
        return {
            'sites': Site.objects.count(),
            'domains': BusinessDomain.objects.count(),
            'processes': BusinessProcess.objects.count(),
            'applications': Application.objects.count(),
            'flows': ApplicationFlow.objects.count(),
            'vms': VirtualMachine.objects.count(),
        }

    def test_import_creates_unified_multi_site_applications(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._write_dataset(tmp)
            call_command('import_it_landscape', tmp, '--create-sites', '--with-infra')

        self.assertEqual(Site.objects.count(), 2)
        self.assertEqual(BusinessDomain.objects.count(), 2)  # one 'Gestion' per site
        self.assertEqual(Application.objects.count(), 2)  # AppFact unified, AppCompta

        app_fact = Application.objects.get(name='AppFact')
        self.assertTrue(app_fact.is_multi_site)
        self.assertEqual(len(app_fact.site_list), 2)
        self.assertEqual(app_fact.criticality, 'critical')
        self.assertTrue(app_fact.interface_facturation)

        flow = ApplicationFlow.objects.get(flow_id='ALP-FLX-001')
        self.assertEqual(flow.source, app_fact)
        self.assertEqual(flow.site.name, 'CH Alpha')

        # VM created, linked and addressed
        vm = VirtualMachine.objects.get(name='alpha-fact-01')
        self.assertIsNotNone(vm.primary_ip4)
        self.assertIn(vm, app_fact.virtual_machines.all())

    def test_import_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._write_dataset(tmp)
            call_command('import_it_landscape', tmp, '--create-sites', '--with-infra')
            first = self._counts()
            call_command('import_it_landscape', tmp, '--create-sites', '--with-infra')

        self.assertEqual(first, self._counts())

    def test_import_skips_unknown_sites_without_create_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._write_dataset(tmp)
            call_command('import_it_landscape', tmp)

        self.assertEqual(Site.objects.count(), 0)
        self.assertEqual(Application.objects.count(), 0)

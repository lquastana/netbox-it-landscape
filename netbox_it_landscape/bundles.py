"""
Modeling bundles for the setup wizard.

Each bundle describes a ready-to-use cartography for a business sector:
domains / processes structure, sample applications, sample infrastructure
(VLANs, virtual machines) and sample application flows.

Bundle content (names, descriptions) is intentionally kept in the sector's
working language (French) — it is referential data, not UI.

Application entries use a short internal ``key`` so that VMs and flows can
reference them inside the bundle definition.
"""
from django.utils.translation import gettext_lazy as _

from .choices import CriticalityChoices, InterfaceTypeChoices

C = CriticalityChoices.CRITICAL
S = CriticalityChoices.STANDARD
ADM = InterfaceTypeChoices.ADMINISTRATIVE
MED = InterfaceTypeChoices.MEDICALE
FAC = InterfaceTypeChoices.FACTURATION
PLA = InterfaceTypeChoices.PLANIFICATION
AUT = InterfaceTypeChoices.AUTRE


SIH_BUNDLE = {
    'label': _('Hospital information system (SIH)'),
    'description': _(
        'French hospital IS modeling: patient administration, EHR, pharmacy, '
        'emergency, imaging, billing, HR and technical tools — with HL7/DICOM '
        'flows through an integration engine (EAI).'
    ),
    'icon': 'mdi-hospital-building',
    'domains': [
        {'name': 'DP Administrative', 'description': 'Gestion administrative du parcours patient.', 'processes': [
            {'name': 'GAP', 'description': 'Gestion Administrative du Patient.'},
        ]},
        {'name': 'DP Commun', 'description': 'Applications transversales DPI, pharmacie.', 'processes': [
            {'name': 'DPI', 'description': 'Dossier patient informatisé et prescriptions.'},
            {'name': 'Pharmacie', 'description': 'Dispensation & traçabilité.'},
        ]},
        {'name': 'DP Spécialités', 'description': 'Applications des spécialités médicales.', 'processes': [
            {'name': 'Urgences', 'description': 'Prise en charge des urgences.'},
            {'name': 'Hospitalisation à domicile', 'description': 'Suivi HAD et tournées.'},
            {'name': 'Spécialités médicales', 'description': 'Cardiologie, oncologie, blocs.'},
        ]},
        {'name': 'Support & logistique', 'description': 'GMAO, stocks et services généraux.', 'processes': [
            {'name': 'GEF / Inventaire', 'description': 'Maintenance et gestion des stocks.'},
        ]},
        {'name': 'Dossier médico-techniques', 'description': 'Imagerie et plateaux techniques.', 'processes': [
            {'name': 'Imagerie', 'description': 'RIS et PACS.'},
            {'name': 'Télémédecine', 'description': 'Téléconsultation.'},
        ]},
        {'name': 'Communication / Collaboration', 'description': 'Bureautique, intranet et GED.', 'processes': [
            {'name': 'Bureautique', 'description': 'Messagerie et agenda.'},
            {'name': 'Portail web externe', 'description': 'Site institutionnel.'},
            {'name': 'GED', 'description': 'Gestion électronique de documents.'},
        ]},
        {'name': 'Gestion', 'description': 'RH, paie, finances et facturation.', 'processes': [
            {'name': 'RH', 'description': 'Dossiers agents et plannings.'},
            {'name': 'Paie', 'description': 'Paie des personnels.'},
            {'name': 'Finances / Budget', 'description': 'Comptabilité générale.'},
            {'name': 'Facturation', 'description': 'Facturation des séjours.'},
        ]},
        {'name': 'Qualité & Risques', 'description': 'Qualité, risques et contrôle de gestion.', 'processes': [
            {'name': 'Qualité / Risque', 'description': 'Signalements et démarche qualité.'},
            {'name': 'Contrôle de gestion', 'description': 'Tableaux de bord de gestion.'},
        ]},
        {'name': 'Efficience / PMSI', 'description': 'Pilotage médico-économique.', 'processes': [
            {'name': 'Requêteur', 'description': 'Analyse et restitution.'},
        ]},
        {'name': 'Échange de données', 'description': 'Interopérabilité et messagerie sécurisée.', 'processes': [
            {'name': 'MSS', 'description': 'Messagerie de santé sécurisée.'},
            {'name': 'EAI', 'description': "Moteur d'intégration."},
        ]},
        {'name': 'Outils techniques', 'description': 'Supervision, ITSM et téléphonie.', 'processes': [
            {'name': 'Supervision SI', 'description': 'Monitoring et gestion de parc.'},
            {'name': 'Téléphonie', 'description': 'Téléphonie IP.'},
        ]},
        {'name': 'Sureté', 'description': 'Sécurité des biens et des personnes.', 'processes': [
            {'name': 'Vidéosurveillance', 'description': 'Protection des sites.'},
        ]},
        {'name': 'Annuaire & ref. internes', 'description': 'Référentiels organisation & finances.', 'processes': [
            {'name': 'Comptes budgétaires', 'description': 'Plan comptable interne.'},
        ]},
    ],
    'applications': [
        {'key': 'GAP', 'name': 'Maincare iGAP', 'process': ('DP Administrative', 'GAP'), 'editor': 'Maincare', 'criticality': C, 'interfaces': [ADM, FAC], 'description': 'Gestion des admissions, identités et mouvements.'},
        {'key': 'ORB', 'name': 'ORBIS DPI', 'process': ('DP Commun', 'DPI'), 'editor': 'Dedalus', 'criticality': C, 'interfaces': [ADM, MED, PLA, AUT], 'description': 'Dossier patient informatisé et prescription connectée.'},
        {'key': 'ORP', 'name': 'ORBIS Planning', 'process': ('DP Commun', 'DPI'), 'editor': 'Dedalus', 'criticality': S, 'interfaces': [ADM, PLA], 'description': 'Planification des ressources médicales et des lits.'},
        {'key': 'PYX', 'name': 'BD Pyxis MedStation', 'process': ('DP Commun', 'Pharmacie'), 'editor': 'Becton Dickinson', 'criticality': S, 'interfaces': [ADM], 'description': 'Armoires sécurisées de dispensation.'},
        {'key': 'SIL', 'name': 'Sillage Médicament', 'process': ('DP Commun', 'Pharmacie'), 'editor': 'SIB', 'criticality': S, 'interfaces': [MED], 'description': 'Circuit du médicament.'},
        {'key': 'URG', 'name': 'ResUrgences', 'process': ('DP Spécialités', 'Urgences'), 'editor': 'Berger-Levrault', 'criticality': C, 'interfaces': [MED, ADM], 'description': 'Dossier de prise en charge des urgences.'},
        {'key': 'HAD', 'name': 'AntHADine', 'process': ('DP Spécialités', 'Hospitalisation à domicile'), 'editor': 'Berger-Levrault', 'criticality': S, 'interfaces': [MED], 'description': 'Dossier HAD et planification des tournées.'},
        {'key': 'NOM', 'name': 'NomadeCare', 'process': ('DP Spécialités', 'Hospitalisation à domicile'), 'editor': 'Telecom Santé', 'criticality': S, 'interfaces': [MED], 'description': 'Application mobile de soins à domicile.'},
        {'key': 'CAR', 'name': 'CardioReport', 'process': ('DP Spécialités', 'Spécialités médicales'), 'editor': 'Viseus', 'criticality': S, 'interfaces': [MED, PLA], 'description': 'Comptes rendus de cardiologie.'},
        {'key': 'ONC', 'name': 'OncoSuite', 'process': ('DP Spécialités', 'Spécialités médicales'), 'editor': 'Inovelan', 'criticality': S, 'interfaces': [MED, PLA], 'description': 'Dossier communicant de cancérologie.'},
        {'key': 'BLO', 'name': 'BlocManager', 'process': ('DP Spécialités', 'Spécialités médicales'), 'editor': 'Evolucare', 'criticality': C, 'interfaces': [MED, PLA], 'description': 'Programmation et traçabilité des blocs.'},
        {'key': 'CRL', 'name': 'CARL Source', 'process': ('Support & logistique', 'GEF / Inventaire'), 'editor': 'CARL Software', 'criticality': S, 'interfaces': [AUT], 'description': 'GMAO et maintenance des équipements.'},
        {'key': 'SAX', 'name': 'Sage X3 Stock', 'process': ('Support & logistique', 'GEF / Inventaire'), 'editor': 'Sage', 'criticality': S, 'interfaces': [ADM], 'description': 'Gestion des stocks et approvisionnements.'},
        {'key': 'CRS', 'name': 'Carestream RIS', 'process': ('Dossier médico-techniques', 'Imagerie'), 'editor': 'Carestream', 'criticality': S, 'interfaces': [MED], 'description': "Gestion des examens d'imagerie."},
        {'key': 'SEC', 'name': 'Sectra PACS', 'process': ('Dossier médico-techniques', 'Imagerie'), 'editor': 'Sectra', 'criticality': C, 'interfaces': [MED], 'description': 'Archivage et diffusion des images.'},
        {'key': 'DOC', 'name': 'Doctolib Téléconsultation', 'process': ('Dossier médico-techniques', 'Télémédecine'), 'editor': 'Doctolib', 'criticality': S, 'interfaces': [MED], 'hosting': 'SaaS', 'description': 'Téléconsultations et prise de rendez-vous.'},
        {'key': 'M36', 'name': 'Microsoft 365', 'process': ('Communication / Collaboration', 'Bureautique'), 'editor': 'Microsoft', 'criticality': C, 'interfaces': [AUT], 'hosting': 'SaaS', 'description': 'Messagerie, bureautique et collaboration.'},
        {'key': 'WPR', 'name': 'WordPress', 'process': ('Communication / Collaboration', 'Portail web externe'), 'editor': 'Automattic', 'criticality': S, 'interfaces': [AUT], 'description': 'Site internet institutionnel.'},
        {'key': 'DWR', 'name': 'DocuWare', 'process': ('Communication / Collaboration', 'GED'), 'editor': 'DocuWare', 'criticality': S, 'interfaces': [ADM], 'description': 'Gestion électronique de documents.'},
        {'key': 'CGR', 'name': 'Cegid HR', 'process': ('Gestion', 'RH'), 'editor': 'Cegid', 'criticality': S, 'interfaces': [ADM], 'description': 'Gestion des ressources humaines.'},
        {'key': 'OCT', 'name': 'Octime', 'process': ('Gestion', 'RH'), 'editor': 'Octime', 'criticality': S, 'interfaces': [ADM], 'description': 'Gestion des temps et plannings.'},
        {'key': 'CGP', 'name': 'Cegid Payroll', 'process': ('Gestion', 'Paie'), 'editor': 'Cegid', 'criticality': C, 'interfaces': [ADM, FAC], 'description': 'Paie des personnels.'},
        {'key': 'SGE', 'name': 'Sage 1000', 'process': ('Gestion', 'Finances / Budget'), 'editor': 'Sage', 'criticality': S, 'interfaces': [ADM, FAC], 'description': 'Comptabilité et finances.'},
        {'key': 'IFC', 'name': 'iFact', 'process': ('Gestion', 'Facturation'), 'editor': 'CPage', 'criticality': C, 'interfaces': [FAC, ADM], 'description': 'Facturation des séjours et actes.'},
        {'key': 'BLU', 'name': 'BlueKanGo QHSE', 'process': ('Qualité & Risques', 'Qualité / Risque'), 'editor': 'BlueKanGo', 'criticality': S, 'interfaces': [AUT], 'hosting': 'SaaS', 'description': 'Qualité, risques et signalements.'},
        {'key': 'MYR', 'name': 'MyReport', 'process': ('Qualité & Risques', 'Contrôle de gestion'), 'editor': 'Report One', 'criticality': S, 'interfaces': [ADM], 'description': 'Reporting de gestion.'},
        {'key': 'TAB', 'name': 'Tableau', 'process': ('Efficience / PMSI', 'Requêteur'), 'editor': 'Salesforce', 'criticality': S, 'interfaces': [ADM], 'description': 'Analyse et visualisation de données.'},
        {'key': 'MAI', 'name': 'Mailiz', 'process': ('Échange de données', 'MSS'), 'editor': 'ANS', 'criticality': S, 'interfaces': [MED, ADM], 'hosting': 'SaaS', 'description': 'Messagerie de santé sécurisée.'},
        {'key': 'ENO', 'name': 'Enovacom Integration Engine', 'process': ('Échange de données', 'EAI'), 'editor': 'Enovacom', 'criticality': C, 'interfaces': [AUT], 'description': "Moteur d'intégration HL7."},
        {'key': 'CEN', 'name': 'Centreon', 'process': ('Outils techniques', 'Supervision SI'), 'editor': 'Centreon', 'criticality': S, 'interfaces': [AUT], 'description': 'Supervision des infrastructures.'},
        {'key': 'GLP', 'name': 'GLPI', 'process': ('Outils techniques', 'Supervision SI'), 'editor': 'Teclib', 'criticality': S, 'interfaces': [AUT], 'description': 'ITSM et gestion de parc.'},
        {'key': 'CCM', 'name': 'Cisco Unified Communications Manager', 'process': ('Outils techniques', 'Téléphonie'), 'editor': 'Cisco', 'criticality': S, 'interfaces': [AUT], 'description': 'Téléphonie IP.'},
        {'key': 'MIL', 'name': 'Milestone XProtect', 'process': ('Sureté', 'Vidéosurveillance'), 'editor': 'Milestone', 'criticality': C, 'interfaces': [AUT], 'description': 'Vidéosurveillance des sites.'},
        {'key': 'SFR', 'name': 'Sage FRP 1000', 'process': ('Annuaire & ref. internes', 'Comptes budgétaires'), 'editor': 'Sage', 'criticality': S, 'interfaces': [ADM], 'description': 'Référentiel budgétaire et comptable.'},
    ],
    'vlans': [
        {'vid': 210, 'name': 'VLAN-ADMIN', 'description': 'Applications administratives et support', 'prefix': '10.{net}.10.0/24', 'gateway': '10.{net}.10.254'},
        {'vid': 220, 'name': 'VLAN-SOINS', 'description': 'DPI, urgences et pharmacie', 'prefix': '10.{net}.20.0/24', 'gateway': '10.{net}.20.254'},
        {'vid': 230, 'name': 'VLAN-IMAGERIE', 'description': 'Imagerie et vidéo', 'prefix': '10.{net}.30.0/24', 'gateway': '10.{net}.30.254'},
        {'vid': 240, 'name': 'VLAN-TECH', 'description': 'Outils techniques et intégration', 'prefix': '10.{net}.40.0/24', 'gateway': '10.{net}.40.254'},
    ],
    'vms': [
        {'name': '{prefix}-gap-01', 'app': 'GAP', 'role': 'Serveur applicatif GAP', 'ip': '10.{net}.10.10', 'vcpus': 4, 'memory': 16384, 'disk': 200},
        {'name': '{prefix}-ifact-01', 'app': 'IFC', 'role': 'Serveur facturation iFact', 'ip': '10.{net}.10.11', 'vcpus': 4, 'memory': 16384, 'disk': 200},
        {'name': '{prefix}-sage-01', 'app': 'SGE', 'role': 'Serveur finances Sage 1000', 'ip': '10.{net}.10.12', 'vcpus': 4, 'memory': 16384, 'disk': 250},
        {'name': '{prefix}-sfr-01', 'app': 'SFR', 'role': 'Référentiel budgétaire Sage FRP', 'ip': '10.{net}.10.13', 'vcpus': 2, 'memory': 8192, 'disk': 100},
        {'name': '{prefix}-carl-01', 'app': 'CRL', 'role': 'GMAO CARL Source', 'ip': '10.{net}.10.14', 'vcpus': 2, 'memory': 8192, 'disk': 100},
        {'name': '{prefix}-sax-01', 'app': 'SAX', 'role': 'Gestion des stocks Sage X3', 'ip': '10.{net}.10.15', 'vcpus': 2, 'memory': 8192, 'disk': 100},
        {'name': '{prefix}-orbis-app-01', 'app': 'ORB', 'role': 'Serveur applicatif ORBIS DPI', 'ip': '10.{net}.20.10', 'vcpus': 8, 'memory': 32768, 'disk': 400},
        {'name': '{prefix}-orbis-db-01', 'app': 'ORB', 'role': 'Base de données ORBIS DPI', 'ip': '10.{net}.20.11', 'vcpus': 8, 'memory': 65536, 'disk': 800},
        {'name': '{prefix}-orbis-plan-01', 'app': 'ORP', 'role': 'Serveur ORBIS Planning', 'ip': '10.{net}.20.12', 'vcpus': 4, 'memory': 16384, 'disk': 200},
        {'name': '{prefix}-pyxis-01', 'app': 'PYX', 'role': 'Serveur BD Pyxis MedStation', 'ip': '10.{net}.20.13', 'vcpus': 2, 'memory': 8192, 'disk': 100},
        {'name': '{prefix}-sillage-01', 'app': 'SIL', 'role': 'Serveur pharmacie Sillage', 'ip': '10.{net}.20.14', 'vcpus': 2, 'memory': 8192, 'disk': 100},
        {'name': '{prefix}-urgences-01', 'app': 'URG', 'role': 'Serveur urgences ResUrgences', 'ip': '10.{net}.20.15', 'vcpus': 4, 'memory': 16384, 'disk': 200},
        {'name': '{prefix}-cardio-01', 'app': 'CAR', 'role': 'Serveur CardioReport', 'ip': '10.{net}.20.16', 'vcpus': 2, 'memory': 8192, 'disk': 100},
        {'name': '{prefix}-onco-01', 'app': 'ONC', 'role': 'Serveur OncoSuite', 'ip': '10.{net}.20.17', 'vcpus': 2, 'memory': 8192, 'disk': 100},
        {'name': '{prefix}-bloc-01', 'app': 'BLO', 'role': 'Serveur BlocManager', 'ip': '10.{net}.20.18', 'vcpus': 4, 'memory': 16384, 'disk': 200},
        {'name': '{prefix}-ris-01', 'app': 'CRS', 'role': 'Serveur RIS Carestream', 'ip': '10.{net}.30.10', 'vcpus': 4, 'memory': 16384, 'disk': 400},
        {'name': '{prefix}-pacs-01', 'app': 'SEC', 'role': 'Serveur PACS Sectra', 'ip': '10.{net}.30.11', 'vcpus': 8, 'memory': 32768, 'disk': 2000},
        {'name': '{prefix}-milestone-01', 'app': 'MIL', 'role': 'Serveur vidéosurveillance Milestone', 'ip': '10.{net}.30.12', 'vcpus': 4, 'memory': 16384, 'disk': 1000},
        {'name': '{prefix}-eai-01', 'app': 'ENO', 'role': 'Serveur EAI Enovacom', 'ip': '10.{net}.40.10', 'vcpus': 4, 'memory': 16384, 'disk': 200},
        {'name': '{prefix}-centreon-01', 'app': 'CEN', 'role': 'Supervision Centreon', 'ip': '10.{net}.40.11', 'vcpus': 2, 'memory': 8192, 'disk': 100},
        {'name': '{prefix}-glpi-01', 'app': 'GLP', 'role': 'ITSM GLPI', 'ip': '10.{net}.40.12', 'vcpus': 2, 'memory': 8192, 'disk': 100},
        {'name': '{prefix}-ucm-01', 'app': 'CCM', 'role': 'Téléphonie IP Cisco UCM', 'ip': '10.{net}.40.13', 'vcpus': 4, 'memory': 16384, 'disk': 200},
    ],
    'flows': [
        {'source': 'GAP', 'target': 'ORB', 'protocol': 'HL7', 'port': 2575, 'message_type': 'ADT', 'interface_type': ADM, 'eai': 'Enovacom Engine', 'description': 'Admissions et mouvements vers le DPI'},
        {'source': 'GAP', 'target': 'IFC', 'protocol': 'HL7', 'port': 2575, 'message_type': 'DFT', 'interface_type': ADM, 'eai': 'Enovacom Engine', 'description': 'Données de séjour pour facturation'},
        {'source': 'CRS', 'target': 'ORB', 'protocol': 'HL7', 'port': 2575, 'message_type': 'ORM', 'interface_type': MED, 'eai': 'Enovacom Engine', 'description': "Demandes d'examens d'imagerie"},
        {'source': 'CRS', 'target': 'SEC', 'protocol': 'DICOM', 'port': 104, 'message_type': 'DICOM', 'interface_type': MED, 'eai': 'Direct', 'description': 'Transfert des images vers le PACS'},
        {'source': 'SIL', 'target': 'ORB', 'protocol': 'HL7', 'port': 2575, 'message_type': 'RDE', 'interface_type': MED, 'eai': 'Enovacom Engine', 'description': 'Ordonnances et délivrances'},
        {'source': 'GAP', 'target': 'MAI', 'protocol': 'SMTP/TLS', 'port': 587, 'message_type': 'MSS', 'interface_type': ADM, 'eai': 'Passerelle MSS', 'description': 'Notifications messagerie sécurisée'},
        {'source': 'ORB', 'target': 'ORP', 'protocol': 'API', 'port': 443, 'message_type': 'Planning', 'interface_type': PLA, 'eai': 'API interne', 'description': 'Synchronisation des plannings'},
        {'source': 'GAP', 'target': 'PYX', 'protocol': 'HL7', 'port': 2575, 'message_type': 'RDE', 'interface_type': ADM, 'eai': 'Enovacom Engine', 'description': 'Identités vers les armoires Pyxis'},
        {'source': 'URG', 'target': 'ORB', 'protocol': 'HL7', 'port': 2575, 'message_type': 'ADT', 'interface_type': MED, 'eai': 'Enovacom Engine', 'description': 'Passages aux urgences vers le DPI'},
        {'source': 'MAI', 'target': 'ORB', 'protocol': 'SMTP/TLS', 'port': 587, 'message_type': 'MSS', 'interface_type': MED, 'eai': 'Passerelle MSS', 'description': 'Courriers entrants vers le DPI'},
        {'source': 'IFC', 'target': 'SGE', 'protocol': 'SFTP', 'port': 22, 'message_type': 'Factures', 'interface_type': FAC, 'eai': 'ETL', 'description': 'Titres de recettes vers la comptabilité'},
        {'source': 'GAP', 'target': 'ENO', 'protocol': 'HL7', 'port': 2575, 'message_type': 'ORM', 'interface_type': ADM, 'eai': 'Enovacom Engine', 'description': "Flux d'orchestration EAI"},
        {'source': 'ORB', 'target': 'CEN', 'protocol': 'HTTPS', 'port': 443, 'message_type': 'Monitoring', 'interface_type': AUT, 'eai': 'API', 'description': 'Supervision applicative du DPI'},
        {'source': 'CAR', 'target': 'ORP', 'protocol': 'API', 'port': 443, 'message_type': 'Planning', 'interface_type': PLA, 'eai': 'API interne', 'description': 'Plages de cardiologie'},
        {'source': 'ONC', 'target': 'ORP', 'protocol': 'API', 'port': 443, 'message_type': 'Planning', 'interface_type': PLA, 'eai': 'API interne', 'description': "Plages d'oncologie"},
        {'source': 'BLO', 'target': 'ORP', 'protocol': 'API', 'port': 443, 'message_type': 'Planning', 'interface_type': PLA, 'eai': 'API interne', 'description': 'Programmation des blocs'},
        {'source': 'CAR', 'target': 'GAP', 'protocol': 'HL7', 'port': 2575, 'message_type': 'DFT', 'interface_type': FAC, 'eai': 'Enovacom Engine', 'description': 'Actes de cardiologie à facturer'},
        {'source': 'ONC', 'target': 'GAP', 'protocol': 'HL7', 'port': 2575, 'message_type': 'DFT', 'interface_type': FAC, 'eai': 'Enovacom Engine', 'description': "Actes d'oncologie à facturer"},
        {'source': 'BLO', 'target': 'GAP', 'protocol': 'HL7', 'port': 2575, 'message_type': 'DFT', 'interface_type': FAC, 'eai': 'Enovacom Engine', 'description': 'Actes de bloc à facturer'},
        {'source': 'DOC', 'target': 'ORB', 'protocol': 'HTTPS', 'port': 443, 'message_type': 'Téléconsultation', 'interface_type': MED, 'eai': 'API', 'description': 'Comptes rendus de téléconsultation'},
        {'source': 'HAD', 'target': 'ORB', 'protocol': 'FHIR', 'port': 443, 'message_type': 'CarePlan', 'interface_type': MED, 'eai': 'API', 'description': 'Plans de soins HAD'},
        {'source': 'GAP', 'target': 'MYR', 'protocol': 'API', 'port': 443, 'message_type': 'Analytics', 'interface_type': ADM, 'eai': 'API', 'description': 'Données de gestion'},
        {'source': 'GAP', 'target': 'TAB', 'protocol': 'API', 'port': 443, 'message_type': 'KPI', 'interface_type': ADM, 'eai': 'API', 'description': 'Indicateurs de pilotage'},
        {'source': 'SGE', 'target': 'SFR', 'protocol': 'API', 'port': 443, 'message_type': 'Comptabilité', 'interface_type': ADM, 'eai': 'API interne', 'description': 'Synchronisation comptable'},
        {'source': 'ENO', 'target': 'GLP', 'protocol': 'HTTPS', 'port': 443, 'message_type': 'Incidents', 'interface_type': AUT, 'eai': 'API', 'description': "Tickets d'incidents d'intégration"},
    ],
}


INDUSTRY_BUNDLE = {
    'label': _('Manufacturing / Industry'),
    'description': _(
        'Industrial IS modeling: ERP, MES, SCADA, warehouse and transport '
        'management, quality (LIMS), PLM, HR — with OPC-UA, EDI and API flows '
        'through an ESB.'
    ),
    'icon': 'mdi-factory',
    'domains': [
        {'name': 'Pilotage & ERP', 'description': "Gestion d'entreprise et processus commerciaux.", 'processes': [
            {'name': 'Gestion commerciale', 'description': 'Devis, commandes et ventes.'},
            {'name': 'Comptabilité & Finance', 'description': 'Comptabilité générale et analytique.'},
        ]},
        {'name': 'Production', 'description': 'Exécution et supervision de la production.', 'processes': [
            {'name': 'Exécution de production', 'description': 'Ordres de fabrication et traçabilité (MES).'},
            {'name': 'Supervision industrielle', 'description': 'SCADA et automatismes.'},
            {'name': 'Maintenance', 'description': 'Maintenance préventive et curative.'},
        ]},
        {'name': 'Supply chain', 'description': 'Logistique amont et aval.', 'processes': [
            {'name': 'Entrepôt', 'description': 'Gestion des stocks et préparation (WMS).'},
            {'name': 'Transport', 'description': 'Planification des expéditions (TMS).'},
            {'name': 'Approvisionnements', 'description': 'Achats et fournisseurs.'},
        ]},
        {'name': 'Qualité & HSE', 'description': 'Qualité produit et sécurité.', 'processes': [
            {'name': 'Laboratoire qualité', 'description': 'Analyses et certificats (LIMS).'},
            {'name': 'HSE', 'description': 'Hygiène, sécurité, environnement.'},
        ]},
        {'name': 'Ingénierie', 'description': 'Conception et données techniques.', 'processes': [
            {'name': 'PLM / CAO', 'description': 'Nomenclatures et cycle de vie produit.'},
        ]},
        {'name': 'RH & Paie', 'description': 'Ressources humaines.', 'processes': [
            {'name': 'RH', 'description': 'Dossiers salariés.'},
            {'name': 'Temps & activités', 'description': 'Badgeage et plannings.'},
        ]},
        {'name': 'IT transverse', 'description': 'Socle technique et intégration.', 'processes': [
            {'name': 'Intégration', 'description': "Bus d'échanges inter-applicatifs (ESB)."},
            {'name': 'Supervision SI', 'description': 'Monitoring et ITSM.'},
            {'name': 'Bureautique', 'description': 'Collaboration et messagerie.'},
        ]},
    ],
    'applications': [
        {'key': 'ERP', 'name': 'SAP S/4HANA', 'process': ('Pilotage & ERP', 'Gestion commerciale'), 'editor': 'SAP', 'criticality': C, 'interfaces': [ADM, FAC], 'description': 'ERP : ventes, achats, stocks, finance.'},
        {'key': 'FIN', 'name': 'Sage FRP 1000 Industrie', 'process': ('Pilotage & ERP', 'Comptabilité & Finance'), 'editor': 'Sage', 'criticality': S, 'interfaces': [ADM, FAC], 'description': 'Consolidation comptable.'},
        {'key': 'MES', 'name': 'Siemens Opcenter MES', 'process': ('Production', 'Exécution de production'), 'editor': 'Siemens', 'criticality': C, 'interfaces': [AUT, PLA], 'description': 'Pilotage des ordres de fabrication et traçabilité.'},
        {'key': 'SCA', 'name': 'AVEVA System Platform', 'process': ('Production', 'Supervision industrielle'), 'editor': 'AVEVA', 'criticality': C, 'interfaces': [AUT], 'description': 'SCADA : supervision temps réel des lignes.'},
        {'key': 'GMA', 'name': 'CARL Source Factory', 'process': ('Production', 'Maintenance'), 'editor': 'CARL Software', 'criticality': S, 'interfaces': [AUT], 'description': 'GMAO des équipements industriels.'},
        {'key': 'WMS', 'name': 'Manhattan WMS', 'process': ('Supply chain', 'Entrepôt'), 'editor': 'Manhattan Associates', 'criticality': C, 'interfaces': [ADM], 'description': "Gestion d'entrepôt et préparation de commandes."},
        {'key': 'TMS', 'name': 'Descartes TMS', 'process': ('Supply chain', 'Transport'), 'editor': 'Descartes', 'criticality': S, 'interfaces': [ADM, PLA], 'hosting': 'SaaS', 'description': 'Planification transport et expéditions.'},
        {'key': 'SRM', 'name': 'Ivalua', 'process': ('Supply chain', 'Approvisionnements'), 'editor': 'Ivalua', 'criticality': S, 'interfaces': [ADM], 'hosting': 'SaaS', 'description': 'Achats et gestion fournisseurs.'},
        {'key': 'LIM', 'name': 'LabWare LIMS', 'process': ('Qualité & HSE', 'Laboratoire qualité'), 'editor': 'LabWare', 'criticality': S, 'interfaces': [AUT], 'description': 'Gestion du laboratoire qualité.'},
        {'key': 'HSE', 'name': 'BlueKanGo HSE', 'process': ('Qualité & HSE', 'HSE'), 'editor': 'BlueKanGo', 'criticality': S, 'interfaces': [AUT], 'hosting': 'SaaS', 'description': 'Signalements HSE et conformité.'},
        {'key': 'PLM', 'name': 'PTC Windchill', 'process': ('Ingénierie', 'PLM / CAO'), 'editor': 'PTC', 'criticality': S, 'interfaces': [AUT], 'description': 'Cycle de vie produit et nomenclatures.'},
        {'key': 'HRM', 'name': 'Cegid HR Ultimate', 'process': ('RH & Paie', 'RH'), 'editor': 'Cegid', 'criticality': S, 'interfaces': [ADM], 'hosting': 'SaaS', 'description': 'RH et paie.'},
        {'key': 'TMP', 'name': 'Kelio', 'process': ('RH & Paie', 'Temps & activités'), 'editor': 'Bodet Software', 'criticality': S, 'interfaces': [ADM], 'description': 'Gestion des temps et badgeage.'},
        {'key': 'ESB', 'name': 'Talend ESB', 'process': ('IT transverse', 'Intégration'), 'editor': 'Qlik', 'criticality': C, 'interfaces': [AUT], 'description': "Bus d'intégration inter-applicatif."},
        {'key': 'CEN', 'name': 'Centreon', 'process': ('IT transverse', 'Supervision SI'), 'editor': 'Centreon', 'criticality': S, 'interfaces': [AUT], 'description': 'Supervision des infrastructures.'},
        {'key': 'M36', 'name': 'Microsoft 365', 'process': ('IT transverse', 'Bureautique'), 'editor': 'Microsoft', 'criticality': S, 'interfaces': [AUT], 'hosting': 'SaaS', 'description': 'Collaboration et messagerie.'},
    ],
    'vlans': [
        {'vid': 310, 'name': 'VLAN-GESTION', 'description': 'ERP, finance, RH et supply chain', 'prefix': '10.{net}.10.0/24', 'gateway': '10.{net}.10.254'},
        {'vid': 320, 'name': 'VLAN-PROD', 'description': 'MES, SCADA et qualité (réseau OT)', 'prefix': '10.{net}.20.0/24', 'gateway': '10.{net}.20.254'},
        {'vid': 330, 'name': 'VLAN-TECH', 'description': 'Intégration et supervision', 'prefix': '10.{net}.30.0/24', 'gateway': '10.{net}.30.254'},
    ],
    'vms': [
        {'name': '{prefix}-erp-app-01', 'app': 'ERP', 'role': 'Serveur applicatif SAP', 'ip': '10.{net}.10.10', 'vcpus': 16, 'memory': 131072, 'disk': 1000},
        {'name': '{prefix}-erp-db-01', 'app': 'ERP', 'role': 'Base HANA', 'ip': '10.{net}.10.11', 'vcpus': 16, 'memory': 262144, 'disk': 2000},
        {'name': '{prefix}-fin-01', 'app': 'FIN', 'role': 'Serveur comptabilité', 'ip': '10.{net}.10.12', 'vcpus': 4, 'memory': 16384, 'disk': 200},
        {'name': '{prefix}-wms-01', 'app': 'WMS', 'role': 'Serveur WMS', 'ip': '10.{net}.10.13', 'vcpus': 8, 'memory': 32768, 'disk': 400},
        {'name': '{prefix}-kelio-01', 'app': 'TMP', 'role': 'Serveur gestion des temps', 'ip': '10.{net}.10.14', 'vcpus': 2, 'memory': 8192, 'disk': 100},
        {'name': '{prefix}-mes-01', 'app': 'MES', 'role': 'Serveur MES', 'ip': '10.{net}.20.10', 'vcpus': 8, 'memory': 32768, 'disk': 400},
        {'name': '{prefix}-scada-01', 'app': 'SCA', 'role': 'Serveur SCADA', 'ip': '10.{net}.20.11', 'vcpus': 8, 'memory': 32768, 'disk': 400},
        {'name': '{prefix}-scada-hist-01', 'app': 'SCA', 'role': 'Historian SCADA', 'ip': '10.{net}.20.12', 'vcpus': 4, 'memory': 16384, 'disk': 1000},
        {'name': '{prefix}-lims-01', 'app': 'LIM', 'role': 'Serveur LIMS', 'ip': '10.{net}.20.13', 'vcpus': 4, 'memory': 16384, 'disk': 200},
        {'name': '{prefix}-gmao-01', 'app': 'GMA', 'role': 'Serveur GMAO', 'ip': '10.{net}.20.14', 'vcpus': 2, 'memory': 8192, 'disk': 100},
        {'name': '{prefix}-plm-01', 'app': 'PLM', 'role': 'Serveur PLM', 'ip': '10.{net}.10.15', 'vcpus': 4, 'memory': 16384, 'disk': 500},
        {'name': '{prefix}-esb-01', 'app': 'ESB', 'role': 'Serveur ESB', 'ip': '10.{net}.30.10', 'vcpus': 4, 'memory': 16384, 'disk': 200},
        {'name': '{prefix}-centreon-01', 'app': 'CEN', 'role': 'Supervision Centreon', 'ip': '10.{net}.30.11', 'vcpus': 2, 'memory': 8192, 'disk': 100},
    ],
    'flows': [
        {'source': 'ERP', 'target': 'MES', 'protocol': 'API/IDoc', 'port': 443, 'message_type': 'Ordres de fabrication', 'interface_type': PLA, 'eai': 'Talend ESB', 'description': 'OF planifiés vers le MES'},
        {'source': 'MES', 'target': 'ERP', 'protocol': 'API/IDoc', 'port': 443, 'message_type': 'Déclarations de production', 'interface_type': ADM, 'eai': 'Talend ESB', 'description': 'Quantités produites et consommations'},
        {'source': 'MES', 'target': 'SCA', 'protocol': 'OPC-UA', 'port': 4840, 'message_type': 'Consignes', 'interface_type': AUT, 'eai': 'Direct', 'description': 'Consignes de production vers les lignes'},
        {'source': 'SCA', 'target': 'MES', 'protocol': 'OPC-UA', 'port': 4840, 'message_type': 'Mesures', 'interface_type': AUT, 'eai': 'Direct', 'description': 'Remontée temps réel des compteurs'},
        {'source': 'ERP', 'target': 'WMS', 'protocol': 'API', 'port': 443, 'message_type': 'Ordres de livraison', 'interface_type': ADM, 'eai': 'Talend ESB', 'description': 'Commandes à préparer'},
        {'source': 'WMS', 'target': 'ERP', 'protocol': 'API', 'port': 443, 'message_type': 'Mouvements de stock', 'interface_type': ADM, 'eai': 'Talend ESB', 'description': 'Stocks et expéditions confirmées'},
        {'source': 'WMS', 'target': 'TMS', 'protocol': 'EDI', 'port': 443, 'message_type': 'Expéditions', 'interface_type': PLA, 'eai': 'Talend ESB', 'description': 'Plans de chargement'},
        {'source': 'ERP', 'target': 'FIN', 'protocol': 'SFTP', 'port': 22, 'message_type': 'Écritures comptables', 'interface_type': FAC, 'eai': 'ETL', 'description': 'Journaux comptables'},
        {'source': 'LIM', 'target': 'MES', 'protocol': 'API', 'port': 443, 'message_type': 'Résultats qualité', 'interface_type': AUT, 'eai': 'Talend ESB', 'description': 'Libération des lots'},
        {'source': 'GMA', 'target': 'MES', 'protocol': 'API', 'port': 443, 'message_type': 'Arrêts maintenance', 'interface_type': PLA, 'eai': 'API interne', 'description': 'Indisponibilités équipements'},
        {'source': 'PLM', 'target': 'ERP', 'protocol': 'API', 'port': 443, 'message_type': 'Nomenclatures', 'interface_type': AUT, 'eai': 'Talend ESB', 'description': 'BOM et gammes vers l’ERP'},
        {'source': 'TMP', 'target': 'HRM', 'protocol': 'API', 'port': 443, 'message_type': 'Temps de présence', 'interface_type': ADM, 'eai': 'API', 'description': 'Heures badgées vers la paie'},
        {'source': 'ERP', 'target': 'SRM', 'protocol': 'API', 'port': 443, 'message_type': 'Demandes d’achat', 'interface_type': ADM, 'eai': 'API', 'description': 'Besoins d’approvisionnement'},
        {'source': 'MES', 'target': 'CEN', 'protocol': 'HTTPS', 'port': 443, 'message_type': 'Monitoring', 'interface_type': AUT, 'eai': 'API', 'description': 'Supervision du MES'},
    ],
}


BUNDLES = {
    'sih': SIH_BUNDLE,
    'industry': INDUSTRY_BUNDLE,
}

# netbox-it-landscape

🇬🇧 [English version](README.md)

Plugin NetBox de **cartographie applicative**, intégration native des
fonctionnalités du projet [it-landscape](https://github.com/lquastana/it-landscape) :
vues **métier**, **applicative** et **flux** — plus synthèse KPI, comparaison
d'établissements et assistant d'initialisation.

## Pourquoi un plugin ?

Le projet it-landscape d'origine fonctionne *à côté* de NetBox (lecture par API +
tags `app:XXX`). Ce plugin déplace la cartographie *dans* NetBox :

| Concept it-landscape | Dans le plugin |
|---|---|
| Établissement | **Site NetBox** (natif) |
| Domaine métier | Modèle `BusinessDomain` (rattaché au site) |
| Processus | Modèle `BusinessProcess` |
| Application (criticité, interfaces…) | Modèle `Application` — **unique dans le référentiel**, rattachée à N processus |
| Drapeau `multiEtablissement` | **Dérivé** : une application liée à des processus de plusieurs sites est multi-site |
| Trigramme (clé de jointure JSON) | **Supprimé** — remplacé par de vraies relations (FK / M2M) |
| Flux applicatif (protocole, message, EAI…) | Modèle `ApplicationFlow` (avec FK établissement) |
| Serveurs liés par tag `app:XXX` | **Relations M2M directes** vers VM / Device |

Bénéfices de l'intégration native : changelog et journal NetBox sur chaque objet,
permissions par objet, recherche globale, API REST + filtres, custom fields,
tags, et panneaux contextuels injectés sur les pages Site / VM / Device.

## Fonctionnalités

- **Vue métier** (`/plugins/it-landscape/metier/`) : établissements → domaines
  (couleurs) → processus → cartes applications avec criticité et interfaces
  actives. Mode détaillé et **mode paysage** condensé, optimisé impression.
- **Vue applicative** (`/plugins/it-landscape/applicatif/`) : applications
  du référentiel avec leurs serveurs (VM/devices), IP et rôles.
- **Vue flux** (`/plugins/it-landscape/cartographie-flux/`) : table filtrable
  (établissement, interface, protocole, EAI) + diagramme SVG source → cible
  coloré par type d'interface.
- **Synthèse KPI** (`/plugins/it-landscape/synthese/`) : compteurs clés,
  points d'attention (critiques sans serveur/supervision…), dépendance EAI,
  applications les plus connectées, top éditeurs.
- **Comparaison d'établissements** (`/plugins/it-landscape/comparaison/`) :
  matrice de similarité (Jaccard), applications déjà mutualisées,
  **opportunités de convergence** (même processus, applications différentes),
  spécificités par établissement.
- **Assistant d'initialisation** (`/plugins/it-landscape/initialisation/`) :
  bundles de modélisation prêts à l'emploi — **SIH** (hôpital : GAP, DPI,
  pharmacie, imagerie… avec flux HL7/DICOM via un EAI) et **Industrie** (ERP,
  MES, SCADA, WMS… avec flux OPC-UA/EDI via un ESB) — structure
  domaines/processus + applications, VLAN, VM et flux d'exemple, en un clic.
- **Multilingue** : interface en anglais, traduction française complète
  (suivant la langue de l'utilisateur NetBox).
- **CRUD complet** : domaines, processus, applications, flux (formulaires,
  filtres, suppression en masse, changelog, journal).
- **API REST** : `/api/plugins/it-landscape/…` (4 endpoints, filtres inclus).
- **Recherche globale NetBox** : applications, flux, domaines, processus indexés.
- **Panneaux contextuels** : applications affichées sur les pages VM / Device,
  synthèse cartographie sur la page Site.
- **Import des données it-landscape** : commande `import_it_landscape`.

## Captures d'écran

### Synthèse KPI

![Synthèse KPI](docs/screenshots/kpi-summary.png)

### Vue métier paysage

![Vue métier paysage](docs/screenshots/business-landscape.png)

### Vue applicative

![Vue applicative](docs/screenshots/application-view.png)

### Vue flux

![Vue flux](docs/screenshots/flow-view.png)

### Comparaison d'établissements

![Comparaison d'établissements](docs/screenshots/facility-comparison.png)

## Installation

```bash
pip install netbox-it-landscape   # ou pip install -e /chemin/vers/le/repo
```

Dans `configuration.py` (ou `/etc/netbox/config/plugins.py` avec netbox-docker) :

```python
PLUGINS = ["netbox_it_landscape"]
```

Puis :

```bash
python manage.py migrate
```

### Développement avec la stack it-landscape (Docker)

Le fichier `docker-compose.override.yml` fourni dans le dépôt it-landscape
monte ce plugin dans le conteneur NetBox, l'installe en mode editable et
l'active. Depuis le dépôt it-landscape :

```bash
docker compose --profile netbox up -d --force-recreate netbox
```

## Import des données existantes

Les fichiers JSON du projet it-landscape (`<etab>.json`, `<etab>.flux.json`,
`<etab>.infra.json`, `trigrammes.json`) s'importent en une commande :

```bash
python manage.py import_it_landscape /opt/it-landscape-data --create-sites --with-infra
```

- Les **sites** sont résolus par nom (`--create-sites` pour créer les manquants).
- Les applications sont **unifiées par nom** : une application présente dans
  plusieurs établissements devient une seule fiche multi-site. Les trigrammes
  des fichiers JSON ne servent que de clé de résolution pendant l'import.
- `--with-infra` crée aussi l'infrastructure de test : **VM** (vCPU, RAM,
  disque, interface eth0, IP primaire, tag `app:XXX`) depuis `*.infra.json`,
  **VLAN, préfixes et passerelles** depuis `*.network.json`.
- Les **VM NetBox** sont rattachées aux applications via les fichiers `*.infra.json`.
- Les applications référencées uniquement par les flux (EAI, supervision…) sont
  créées dans un domaine « Hors référentiel métier ».
- La commande est **idempotente** (relançable sans doublons).

## Compatibilité

- NetBox ≥ 4.0 (testé sur 4.3)
- Python ≥ 3.10

## Licence

MIT

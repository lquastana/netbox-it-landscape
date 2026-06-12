# netbox-it-landscape

Plugin NetBox de **cartographie applicative hospitalière**, intégration native des
fonctionnalités du projet [it-landscape](https://github.com/lquastana/it-landscape) :
vues **métier**, **applicative** et **flux**.

## Pourquoi un plugin ?

Le projet it-landscape d'origine fonctionne *à côté* de NetBox (lecture par API +
tags `app:XXX`). Ce plugin déplace la cartographie *dans* NetBox :

| Concept it-landscape | Dans le plugin |
|---|---|
| Établissement | **Site NetBox** (natif) |
| Domaine métier | Modèle `BusinessDomain` (rattaché au site) |
| Processus | Modèle `BusinessProcess` |
| Application (trigramme, criticité, interfaces…) | Modèle `Application` |
| Flux applicatif (protocole, message, EAI…) | Modèle `ApplicationFlow` |
| Serveurs liés par tag `app:XXX` | **Relations M2M directes** vers VM / Device |

Bénéfices de l'intégration native : changelog et journal NetBox sur chaque objet,
permissions par objet, recherche globale, API REST + filtres, custom fields, tags,
et panneaux contextuels injectés sur les pages Site / VM / Device.

## Fonctionnalités

- **Vue métier** (`/plugins/it-landscape/metier/`) : établissements → domaines
  (couleurs) → processus → cartes applications avec criticité et interfaces actives.
- **Vue applicative** (`/plugins/it-landscape/applicatif/`) : applications
  regroupées par trigramme avec leurs serveurs (VM/devices), IP et rôles.
- **Vue flux** (`/plugins/it-landscape/cartographie-flux/`) : table filtrable
  (établissement, interface, protocole, EAI) + diagramme SVG source → cible
  coloré par type d'interface.
- **CRUD complet** : domaines, processus, applications, flux (formulaires,
  filtres, suppression en masse, changelog, journal).
- **API REST** : `/api/plugins/it-landscape/…` (4 endpoints, filtres inclus).
- **Recherche globale NetBox** : applications, flux, domaines, processus indexés.
- **Panneaux contextuels** : applications affichées sur les pages VM / Device,
  synthèse cartographie sur la page Site.
- **Import des données it-landscape** : commande `import_it_landscape`.

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

Le fichier [`docker-compose.override.yml`](https://github.com/lquastana/it-landscape)
fourni dans le dépôt it-landscape monte ce plugin dans le conteneur NetBox,
l'installe en mode editable et l'active. Depuis le dépôt it-landscape :

```bash
docker compose --profile netbox up -d --force-recreate netbox
```

## Import des données existantes

Les fichiers JSON du projet it-landscape (`<etab>.json`, `<etab>.flux.json`,
`<etab>.infra.json`, `trigrammes.json`) s'importent en une commande :

```bash
python manage.py import_it_landscape /opt/it-landscape-data --create-sites
```

- Les **sites** sont résolus par nom (`--create-sites` pour créer les manquants).
- Les **VM NetBox** sont rattachées aux applications via les fichiers `*.infra.json`.
- Les applications référencées uniquement par les flux (EAI, supervision…) sont
  créées dans un domaine « Hors référentiel métier ».
- La commande est **idempotente** (relançable sans doublons).

## Compatibilité

- NetBox ≥ 4.0 (testé sur 4.3)
- Python ≥ 3.10

## Licence

MIT

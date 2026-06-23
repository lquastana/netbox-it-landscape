# Changelog

All notable changes to this project are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [0.3.0] - 2026-06-17

### Added
- **Cascade impact simulator** (`/cascade/simulateur/`): build an incident
  scenario from one or more failed components (application, application flow,
  virtual machine, device, hosting provider) with a severity per component
  (down / degraded / latency / intermittent). The simulator propagates the
  impact through application flows (BFS, attenuated by depth and interface
  type) and reports impacted applications and business processes grouped by
  site, blocked flows, the causes per application and recommended actions.
  Read-only, gated by the `view_application` permission.
- Tests for the cascade simulator (permission gating, empty scenario, BFS
  propagation), bringing the suite to 19 tests.

### Fixed
- Cascade simulator: adding a second component or clearing the scenario no
  longer breaks the rendering of the selected-components list.
- French translation pass: corrected stale/duplicated strings and translated
  the cascade simulator UI and filter labels.

## [0.2.0] - 2026-06-12

### Added
- **Security**: landscape views now require NetBox object permissions
  (`view_application` / `view_applicationflow`); the setup wizard enforces
  per-option permissions (dcim/ipam/virtualization/extras `add` rights for
  the sample infrastructure, `dcim.add_site` for site creation).
- **Setup wizard** (`/initialisation/`) with two modeling bundles:
  Hospital IS (SIH) and Manufacturing — structure, sample applications,
  infrastructure (VLANs, prefixes, gateways, VMs with primary IPs) and flows.
  Each run is recorded in the target site's journal.
- **Facility comparison** (`/comparaison/`): Jaccard similarity matrix,
  mutualized applications, convergence opportunities, facility-specific apps.
- **KPI summary** (`/synthese/`): key counters, attention points, EAI
  dependency, most connected applications, top vendors.
- **Internationalization**: English source strings with a full French
  translation, following the NetBox user language preference.
- **Condensed landscape mode** on the business view (print-friendly).
- **Test suite** (13 tests) and **GitHub Actions CI** (ruff + tests against
  NetBox 4.3 / 4.4, 4.5 experimental).

### Changed
- Applications are **unique in the referential** and attached to several
  business processes (M2M); the multi-site flag is now derived.
- Application flows carry their own facility FK.
- The flow view displays application names; `views.py` split into a package.

### Removed
- The `trigramme` field (replaced by real relations; still accepted as a
  resolution key by the JSON import command).

## [0.1.0] - 2026-06-12

### Added
- Initial release: BusinessDomain / BusinessProcess / Application /
  ApplicationFlow models, business / application / flow landscape views,
  full CRUD, REST API, global search, Site/VM/Device contextual panels,
  `import_it_landscape` management command.

# Roadmap

Issues and PRs tracked at https://github.com/lquastana/netbox-it-landscape.

## v0.3 — Performance & robustness

> Target: KPI and comparison views handling 1 000+ apps without degradation.

**Performance (identified in audit)**

- Replace Python in-memory KPI calculations with SQL aggregates
  (`annotate(Count(...))`, `values(...).annotate(...)` for criticality
  breakdown, server coverage, top vendors, EAI distribution, flow hubs).
- Replace Python Jaccard computation with a set-based SQL query
  (or at least cap the comparison to 20 sites and document the limit).
- Limit the flow diagram (`_build_diagram`) to 150 nodes by default;
  add a `?limit=` parameter and a warning banner when the cap is hit.
- Cache filter dropdown values (protocols / EAIs) with a short TTL
  instead of two full-table scans per page load.

**Correctness**

- Add a DB constraint (or form validator) preventing `ApplicationFlow.site`
  from being set to a site where neither `source` nor `target` is deployed.
- Guard the `Application.site_list` property against accidental N+1 queries
  outside a prefetch context (raise `AssertionError` in DEBUG, document
  required prefetch chain).

**Tests**

- API CRUD tests for all 4 endpoints.
- Unit tests for KPI calculations (criticality %, server coverage, hub degree).
- Unit tests for `ComparisonLandscapeView` (Jaccard matrix, opportunities).
- Unit tests for `_build_diagram` (node/edge counts, empty input).
- Filter tests for `ApplicationFilterSet` and `ApplicationFlowFilterSet`.

---

## v0.4 — Security hardening

- Replace `monitoring_url = URLField` with a validator that rejects
  `javascript:` and `data:` schemes.
- Audit SVG template rendering: ensure application names inside `<title>`
  and node labels are HTML-escaped (no `| safe` filter on user-controlled
  content).
- Add a `SECURITY.md` with a responsible-disclosure contact.
- Enforce a maximum length on `ApplicationFlow.eai` / `protocol` in forms
  to prevent oversized inputs reaching the SVG renderer.

---

## v0.5 — Extensibility

- **Dynamic interface types**: replace the 5 hardcoded boolean columns
  (`interface_administrative`, …) with a M2M to a configurable
  `InterfaceType` model. Migration path: auto-migrate existing boolean
  flags into M2M entries.
- **Additional bundles**: Retail (ERP/WMS/POS), Public sector, Energy
  (SCADA/DMS).
- **Custom field support in the wizard**: allow passing key/value pairs
  that are set as NetBox custom fields on created objects.
- **Export**: CSV export for the business view table and the flow table
  (complement to the existing print-friendly landscape mode).

---

## v1.0 — Production-grade

- Test coverage ≥ 80 % (tracked in CI via `coverage` + `codecov`).
- Performance benchmarks included in CI (flag regressions > 2×
  against a 500-app fixture).
- Full API documentation (auto-generated OpenAPI spec pinned in docs).
- Data migration guide from the standalone it-landscape JSON format to
  this plugin (complement the existing `import_it_landscape` command
  with a step-by-step doc).
- NetBox 5.x compatibility (track upstream beta and add to CI matrix
  as experimental when available).
- Declare `django-filter` and `netbox` version bounds in
  `[project.dependencies]` once the NetBox plugin API stabilizes.

---

## Backlog (no milestone yet)

- Dark-mode-aware SVG colors in the flow diagram.
- Contextual panel on `IPAddress` pages (show the application using that IP).
- Bulk-edit for `Application.criticality` and `Application.referent`.
- GraphQL support (NetBox Graphene layer).
- Webhook / event-rule triggers on Application criticality change.

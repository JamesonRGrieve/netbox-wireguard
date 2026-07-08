# netbox-wireguard — Agent Operating Guide

Adapted from `../netbox-pf`'s `CLAUDE.md` (same engineering + test discipline), a
**NetBox 4.6 Django plugin**.

`netbox-wireguard` is an **AGPL-3.0** NetBox plugin: a **native source of truth for the
non-secret topology of WireGuard tunnels and peers** on OPNsense/pfSense (and any host
modeled as a `dcim.Device`). It models interfaces, ports, addresses, public keys,
allowed-IPs, and endpoints as explicit columns, so the `ansible-tofu` reconcilers read
the intended topology back 1:1 — without it living in `config_context`.

**Secrets never enter this plugin.** WireGuard private keys and per-peer pre-shared keys
live in **OpenBao** and are injected at apply time. The models hold only non-secret
fields plus a `WireGuardPeer.has_preshared_key` boolean flag — the existence of a PSK,
never its value.

---

## Key Directives / Rules

### DO, ALWAYS:
- If functionality won't work without a parameter, make it a **required positional**
  parameter — never an optional one with an inline presence check.
- Any time you modify a source file, ensure its accompanying test under
  `netbox_wireguard/tests/` contains **comprehensive tests for the change WITHOUT
  MOCKS**, so `manage.py test netbox_wireguard` discovers them, and update any `.md` in
  the same directory that references the changed code.
- Write concise code (avoid obvious comments; use one-liners where possible).
- Critically analyze requirements and ask all necessary clarifying questions before
  implementing or refactoring.
- Phrase documentation for yourself (AI) and for autistic/ADHD humans: a clear
  architectural summary you could reconstruct the code from with 95% accuracy, with
  minimal snippets — **not** usage examples (the browsable REST/GraphQL schema is the
  usage reference).

### DO NOT, EVER, UNDER ANY CIRCUMSTANCE:
- **Add a secret field** (`private_key`, `preshared_key`, or any key/passphrase value).
  Secrets live in OpenBao; this plugin models only non-secret topology plus the
  `has_preshared_key` flag.
- Make assumptions, or answer with "is likely", "probably", or "might be".
- Use frame-local or thread-local state instead of passing data via parameters.
- Skip a failing test instead of fixing the root cause.
- Fix broken functionality while keeping the broken path as a fallback.
- Re-implement existing functionality in a second location to bypass the original.
- Use bandaid fixes instead of fixing the core functionality.
- **Mock the database, the ORM, the NetBox API test client, or any integration path.**
  Tests run against a **real test database** via NetBox's Django test framework — use
  real model instances and real API requests. Only pure utility functions may use mocks.

### Python / Django Guidelines:
- Import children of `datetime`: `from datetime import date` — **never** `import
  datetime` then `datetime.date`.
- Imports are package-relative inside `netbox_wireguard` (`from .models import
  WireGuardTunnel`), never `from netbox_wireguard.models import ...`.
- Models inherit `netbox.models.NetBoxModel` (custom fields, tags, journaling, change
  logging, GraphQL — for free).
- **SPDX header on every source file**: `# SPDX-License-Identifier: AGPL-3.0-or-later`.

### Documentation Guidelines:
- Markdown docs are concise: reconstruct-the-code-with-95%-accuracy architectural
  summaries with minimal snippets, not usage tutorials.

---

## Architecture (NetBox 4.6 plugin)

| File | Responsibility |
|------|----------------|
| `__init__.py` | `PluginConfig` — name `netbox_wireguard`, `base_url='wireguard'`, min/max NetBox version |
| `models.py` | `WireGuardTunnel`, `WireGuardPeer` — the non-secret WireGuard topology |
| `migrations/` | schema migrations — hand-authored (NetBox disables `makemigrations` in prod); verify with `makemigrations --check --dry-run` on a dev NetBox |
| `api/serializers.py`, `api/views.py`, `api/urls.py` | REST API (`NetBoxModelViewSet`) — endpoints at `/api/plugins/wireguard/tunnels/` and `/api/plugins/wireguard/peers/` |
| `filtersets.py` | `NetBoxModelFilterSet` per model (drives API + UI filtering) |
| `tables.py`, `forms.py`, `navigation.py`, `views.py`, `urls.py`, `templates/` | UI layer |
| `graphql/` | GraphQL types (optional) |

### Model — the non-secret WireGuard SoT
- **`WireGuardTunnel`**: `device` FK + `name` + `listen_port` + `address` (interface
  CIDR, may be blank) + `public_key` (non-secret) + `mtu` + `description` + `enabled`.
  Unique per `(device, name)`.
- **`WireGuardPeer`**: `tunnel` FK + `name` + `public_key` + `endpoint` +
  `endpoint_port` + `allowed_ips` (multi-value, one CIDR per line / comma-separated) +
  `persistent_keepalive` + `has_preshared_key` (flag) + `description` + `enabled`.
  Unique per `(tunnel, name)`.

---

## Testing (NO MOCKS — real DB, NetBox test framework)

- Tests live in `netbox_wireguard/tests/`, one module per source module
  (`test_models.py`, `test_api.py`, …).
- Use NetBox's base classes from `utilities.testing`: `ModelViewTestCase` /
  `ViewTestCases`, `APIViewTestCases.APIViewTestCase`, `ChangeLoggedFilterSetTests`.
  They exercise models, API, and filters against a **real test database** — no mocks.
- **Never skip a failing test** — fix the root cause.
- **Run**: `python /opt/netbox/app/netbox/manage.py test netbox_wireguard --keepdb -v2`
  (or `pytest` with `pytest-django` + `DJANGO_SETTINGS_MODULE=netbox.settings`).
- **Coverage bar**: every model, serializer, filterset, and view has tests.

---

## Licensing
- **AGPL-3.0-or-later** (workspace production-IaC standard). SPDX header in every file.

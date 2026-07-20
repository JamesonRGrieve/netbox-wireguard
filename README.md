<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
# netbox-wireguard

A NetBox 4.6 plugin: a **native source of truth for WireGuard tunnel and peer
topology** on OPNsense/pfSense (and any other WireGuard host modeled as a NetBox
`dcim.Device`).

It holds the **non-secret** shape of a WireGuard deployment — interfaces, ports,
addresses, public keys, allowed-IPs, endpoints — as explicit NetBox columns, so the
`ansible-tofu` reconcilers can read the intended topology back 1:1 without it living in
`config_context` or a sidecar file.

## Why

WireGuard config splits cleanly into two halves:

- **Secret half** — the tunnel private key and the per-peer pre-shared key. These are
  **never** stored here; they live in OpenBao and are injected at apply time.
- **Non-secret half** — everything else: which device hosts which tunnel, the listen
  port, the tunnel interface CIDR, the tunnel public key, and each peer's public key,
  allowed-IPs, endpoint, and keepalive. That is topology, and topology belongs in
  NetBox as native objects.

This plugin models only that non-secret half. A `WireGuardPeer.has_preshared_key`
boolean flags *that* a PSK exists (so reconcilers know to fetch one from OpenBao)
without ever holding the value.

## Model

- **WireGuardTunnel** — `device` FK + `name` (e.g. `tun_wg0`) + `listen_port` +
  `address` (interface CIDR, may be blank) + `public_key` (non-secret) + `mtu` +
  `description` + `enabled`. Interface assignment (opt-in): `assign_interface` (bool) +
  `interface_name` (stable descr rules target, e.g. `WG_RW`) + `wg_instance`
  (→ device `wg<instance>`); `interface_name` and `wg_instance` are required when
  `assign_interface` is set (model `clean()`), so the `ansible-tofu` reconciler can
  assign the tunnel as an OPNsense/pfSense interface and resolve rule targets by name.
  Unique per `(device, name)`.
- **WireGuardPeer** — `tunnel` FK + `name` (peer descr) + `public_key` + `endpoint` +
  `endpoint_port` + `allowed_ips` (one CIDR per line / comma-separated) +
  `persistent_keepalive` + `has_preshared_key` (flag only) + `description` + `enabled`.
  Unique per `(tunnel, name)`.

Both inherit `NetBoxModel` (custom fields, tags, change logging, GraphQL, REST API).

**No secret fields.** There is deliberately no `private_key` or `preshared_key` value
column — those live in OpenBao.

## Install

```bash
uv pip install --python /opt/netbox/venv/bin/python netbox-wireguard   # or: pip install -e .
# add "netbox_wireguard" to PLUGINS in configuration.py
python manage.py migrate netbox_wireguard
python manage.py collectstatic --no-input
systemctl restart netbox netbox-rq
```

## Develop / test

Tests run against a **real NetBox test database** (no mocks) via NetBox's Django test
framework. See `CLAUDE.md`.

```bash
python /opt/netbox/app/netbox/manage.py test netbox_wireguard --keepdb -v2
```

## License

AGPL-3.0-or-later.

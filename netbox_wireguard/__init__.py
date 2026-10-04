# SPDX-License-Identifier: AGPL-3.0-or-later
"""netbox-wireguard: a native NetBox source of truth for the **non-secret** topology of
WireGuard tunnels and peers on OPNsense/pfSense, or any host modeled as a ``dcim.Device`` or a
``virtualization.VirtualMachine``.

WireGuard config splits into a secret half (the tunnel private key + per-peer pre-shared
keys) and a non-secret half (interfaces, ports, addresses, public keys, allowed-IPs,
endpoints). The secret half lives in **OpenBao** and is injected at apply time; this
plugin models only the non-secret half so the ansible-tofu reconcilers read the intended
topology back 1:1 — without it living in ``config_context``. A ``has_preshared_key``
boolean flags *that* a PSK exists, never its value.
"""
from netbox.plugins import PluginConfig

__version__ = "0.2.0"


class NetBoxWireGuardConfig(PluginConfig):
    name = "netbox_wireguard"
    verbose_name = "NetBox WireGuard"
    description = "Native SoT for non-secret WireGuard tunnel + peer topology"
    version = __version__
    author = "Jameson"
    base_url = "wireguard"
    min_version = "4.6.0"
    max_version = "4.6.99"


config = NetBoxWireGuardConfig

# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem

_tunnels = PluginMenuItem(
    link="plugins:netbox_wireguard:wireguardtunnel_list",
    link_text="Tunnels",
    buttons=[PluginMenuButton("plugins:netbox_wireguard:wireguardtunnel_add", "Add", "mdi mdi-plus-thick")],
)
_peers = PluginMenuItem(
    link="plugins:netbox_wireguard:wireguardpeer_list",
    link_text="Peers",
    buttons=[PluginMenuButton("plugins:netbox_wireguard:wireguardpeer_add", "Add", "mdi mdi-plus-thick")],
)

menu = PluginMenu(
    label="WireGuard",
    groups=(("WireGuard", (_tunnels, _peers)),),
    icon_class="mdi mdi-vpn",
)

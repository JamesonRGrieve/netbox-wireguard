# SPDX-License-Identifier: AGPL-3.0-or-later
import django_tables2 as tables
from netbox.tables import NetBoxTable, columns
from .models import WireGuardPeer, WireGuardTunnel


class WireGuardTunnelTable(NetBoxTable):
    device = tables.Column(linkify=True)
    name = tables.Column(linkify=True)
    enabled = columns.BooleanColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_wireguard:wireguardtunnel_list")

    class Meta(NetBoxTable.Meta):
        model = WireGuardTunnel
        fields = (
            "pk", "id", "device", "name", "listen_port", "address", "public_key", "mtu",
            "enabled", "description", "tags", "created", "last_updated",
        )
        default_columns = ("device", "name", "listen_port", "address", "enabled")


class WireGuardPeerTable(NetBoxTable):
    tunnel = tables.Column(linkify=True)
    name = tables.Column(linkify=True)
    has_preshared_key = columns.BooleanColumn()
    enabled = columns.BooleanColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_wireguard:wireguardpeer_list")

    class Meta(NetBoxTable.Meta):
        model = WireGuardPeer
        fields = (
            "pk", "id", "tunnel", "name", "public_key", "endpoint", "endpoint_port",
            "allowed_ips", "persistent_keepalive", "has_preshared_key", "enabled",
            "description", "tags", "created", "last_updated",
        )
        default_columns = ("tunnel", "name", "endpoint", "allowed_ips", "has_preshared_key", "enabled")

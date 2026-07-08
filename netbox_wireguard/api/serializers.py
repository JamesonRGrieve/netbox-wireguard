# SPDX-License-Identifier: AGPL-3.0-or-later
from dcim.api.serializers import DeviceSerializer
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers
from ..models import WireGuardPeer, WireGuardTunnel


class WireGuardTunnelSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_wireguard-api:wireguardtunnel-detail")
    device = DeviceSerializer(nested=True)

    class Meta:
        model = WireGuardTunnel
        fields = [
            "id", "url", "display", "device", "name", "listen_port", "address",
            "public_key", "mtu", "description", "enabled",
            "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "device", "name"]


class WireGuardPeerSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_wireguard-api:wireguardpeer-detail")
    tunnel = WireGuardTunnelSerializer(nested=True)

    class Meta:
        model = WireGuardPeer
        fields = [
            "id", "url", "display", "tunnel", "name", "public_key", "endpoint",
            "endpoint_port", "allowed_ips", "persistent_keepalive", "has_preshared_key",
            "description", "enabled",
            "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "tunnel", "name"]

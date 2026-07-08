# SPDX-License-Identifier: AGPL-3.0-or-later
"""REST API CRUD tests against a real DB + real API client (no mocks).

Endpoints are mounted at /api/plugins/wireguard/tunnels/ and /api/plugins/wireguard/peers/.
"""
from utilities.testing import APIViewTestCases, create_test_device
from netbox_wireguard.models import WireGuardPeer, WireGuardTunnel


class _CRUD(
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
):
    pass


class WireGuardTunnelAPITest(_CRUD):
    model = WireGuardTunnel
    brief_fields = ["device", "display", "id", "name", "url"]
    bulk_update_data = {"enabled": False}

    @classmethod
    def setUpTestData(cls):
        device = create_test_device("fw1")
        WireGuardTunnel.objects.bulk_create([
            WireGuardTunnel(device=device, name="tun_wg0", listen_port=51820, address="172.20.20.254/24"),
            WireGuardTunnel(device=device, name="tun_wg1", listen_port=51821),
            WireGuardTunnel(device=device, name="tun_wg2"),
        ])
        cls.create_data = [
            {"device": device.pk, "name": "tun_wg10", "listen_port": 51830,
             "address": "10.10.10.1/24", "public_key": "pubkey10", "mtu": 1420},
            {"device": device.pk, "name": "tun_wg11", "listen_port": 51831},
            {"device": device.pk, "name": "tun_wg12", "enabled": False},
        ]


class WireGuardPeerAPITest(_CRUD):
    model = WireGuardPeer
    brief_fields = ["display", "id", "name", "tunnel", "url"]
    bulk_update_data = {"enabled": False}

    @classmethod
    def setUpTestData(cls):
        device = create_test_device("fw1")
        tunnel = WireGuardTunnel.objects.create(
            device=device, name="tun_wg0", listen_port=51820, address="172.20.20.254/24",
        )
        WireGuardPeer.objects.bulk_create([
            WireGuardPeer(tunnel=tunnel, name="desktop", public_key="pk1",
                          endpoint="desktop.example.com", endpoint_port=51820,
                          allowed_ips="172.20.20.1/32"),
            WireGuardPeer(tunnel=tunnel, name="phone", public_key="pk2", has_preshared_key=True),
            WireGuardPeer(tunnel=tunnel, name="site", public_key="pk3",
                          allowed_ips="10.0.0.0/24\n192.168.50.0/24"),
        ])
        cls.create_data = [
            {"tunnel": tunnel.pk, "name": "laptop", "public_key": "pk10",
             "endpoint": "laptop.example.com", "endpoint_port": 51820, "allowed_ips": "172.20.20.2/32"},
            {"tunnel": tunnel.pk, "name": "tablet", "public_key": "pk11",
             "has_preshared_key": True, "persistent_keepalive": 25},
            {"tunnel": tunnel.pk, "name": "branch", "public_key": "pk12",
             "allowed_ips": "10.1.0.0/16", "enabled": False},
        ]

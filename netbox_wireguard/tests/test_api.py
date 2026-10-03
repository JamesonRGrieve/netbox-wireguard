# SPDX-License-Identifier: AGPL-3.0-or-later
"""REST API CRUD tests against a real DB + real API client (no mocks).

Endpoints are mounted at /api/plugins/wireguard/tunnels/ and /api/plugins/wireguard/peers/.
"""
from utilities.testing import APIViewTestCases, create_test_device
from virtualization.models import Cluster, ClusterType, VirtualMachine
from netbox_wireguard.models import WireGuardPeer, WireGuardTunnel


# A tuple of bases, not a base class: a TestCase subclass with no model would itself be
# collected and every inherited test would error.
_CRUD = (
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
)
# Plugin API URLs live under the `plugins-api` namespace; NetBox appends `-api`.
VIEW_NAMESPACE = "plugins-api:netbox_wireguard"


class WireGuardTunnelAPITest(*_CRUD):
    view_namespace = VIEW_NAMESPACE
    model = WireGuardTunnel
    brief_fields = ["device", "display", "id", "name", "url", "virtual_machine"]
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


class WireGuardVMTunnelAPITest(*_CRUD):
    """Tunnels hosted on a virtual machine (e.g. a guest's own VPN client)."""
    view_namespace = VIEW_NAMESPACE
    model = WireGuardTunnel
    brief_fields = ["device", "display", "id", "name", "url", "virtual_machine"]
    bulk_update_data = {"dns": "10.128.0.1"}

    @classmethod
    def setUpTestData(cls):
        cluster_type = ClusterType.objects.create(name="ct1", slug="ct1")
        vm = VirtualMachine.objects.create(
            name="vm1", cluster=Cluster.objects.create(name="cluster1", type=cluster_type),
        )
        WireGuardTunnel.objects.bulk_create([
            WireGuardTunnel(virtual_machine=vm, name="wg-airvpn1", address="10.150.0.2/32"),
            WireGuardTunnel(virtual_machine=vm, name="wg-airvpn2"),
            WireGuardTunnel(virtual_machine=vm, name="wg-airvpn3"),
        ])
        cls.create_data = [
            {"virtual_machine": vm.pk, "name": "wg-a", "address": "10.150.0.5/32",
             "dns": "10.128.0.1", "mtu": 1320},
            {"virtual_machine": vm.pk, "name": "wg-b", "wg_instance": 2},
            {"virtual_machine": vm.pk, "name": "wg-c", "enabled": False},
        ]


class WireGuardPeerAPITest(*_CRUD):
    view_namespace = VIEW_NAMESPACE
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

# SPDX-License-Identifier: AGPL-3.0-or-later
"""Model tests against a real DB (no mocks): creation, str, constraints, FK behaviour."""
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError
from django.test import TestCase
from utilities.testing import create_test_device
from virtualization.models import Cluster, ClusterType, VirtualMachine
from netbox_wireguard.models import WireGuardPeer, WireGuardTunnel


class WireGuardTunnelModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.device = create_test_device("fw1")

    def test_create_str_and_url(self):
        t = WireGuardTunnel.objects.create(
            device=self.device, name="tun_wg0", listen_port=51820,
            address="172.20.20.254/24", public_key="abc123",
        )
        self.assertEqual(str(t), f"{self.device}: tun_wg0")
        self.assertIn("/plugins/wireguard/tunnels/", t.get_absolute_url())

    def test_defaults_and_optional_blank_address(self):
        t = WireGuardTunnel.objects.create(device=self.device, name="tun_wg1")
        self.assertTrue(t.enabled)
        self.assertIsNone(t.listen_port)
        self.assertIsNone(t.mtu)
        self.assertEqual(t.address, "")
        self.assertEqual(t.public_key, "")

    def test_unique_device_name(self):
        WireGuardTunnel.objects.create(device=self.device, name="tun_wg0")
        with self.assertRaises(IntegrityError), transaction.atomic():
            WireGuardTunnel.objects.create(device=self.device, name="tun_wg0", listen_port=51821)

    def test_same_name_different_device_allowed(self):
        other = create_test_device("fw2")
        WireGuardTunnel.objects.create(device=self.device, name="tun_wg0")
        t = WireGuardTunnel.objects.create(device=other, name="tun_wg0")
        self.assertEqual(t.name, "tun_wg0")

    def test_no_secret_fields(self):
        """Topology only: the model must NOT expose a private key column."""
        field_names = {f.name for f in WireGuardTunnel._meta.get_fields()}
        self.assertNotIn("private_key", field_names)

    def test_interface_assignment_defaults(self):
        t = WireGuardTunnel.objects.create(device=self.device, name="tun_wg0")
        self.assertFalse(t.assign_interface)
        self.assertEqual(t.interface_name, "")
        self.assertIsNone(t.wg_instance)

    def test_assigned_interface_valid(self):
        t = WireGuardTunnel(
            device=self.device, name="tun_wg0", assign_interface=True,
            interface_name="WG_RW", wg_instance=0,
        )
        t.full_clean()  # must not raise; wg_instance=0 (wg0) is valid, not "missing"
        t.save()
        self.assertEqual(t.interface_name, "WG_RW")
        self.assertEqual(t.wg_instance, 0)

    def test_dns_defaults_blank_and_roundtrips(self):
        t = WireGuardTunnel.objects.create(device=self.device, name="tun_wg0")
        self.assertEqual(t.dns, "")
        t.dns = "10.128.0.1, fd7d:76ee:e68f:a993::1"
        t.save()
        t.refresh_from_db()
        self.assertEqual(t.dns, "10.128.0.1, fd7d:76ee:e68f:a993::1")

    def test_assign_interface_requires_name_and_instance(self):
        t = WireGuardTunnel(device=self.device, name="tun_wg0", assign_interface=True)
        with self.assertRaises(ValidationError) as ctx:
            t.full_clean()
        self.assertIn("interface_name", ctx.exception.message_dict)
        self.assertIn("wg_instance", ctx.exception.message_dict)


class WireGuardTunnelHostTest(TestCase):
    """A tunnel lives on exactly one host: a device or a virtual machine."""

    @classmethod
    def setUpTestData(cls):
        cls.device = create_test_device("fw1")
        cluster_type = ClusterType.objects.create(name="ct1", slug="ct1")
        cluster = Cluster.objects.create(name="cluster1", type=cluster_type)
        cls.vm = VirtualMachine.objects.create(name="vm1", cluster=cluster)

    def test_vm_host_str_and_host(self):
        t = WireGuardTunnel.objects.create(virtual_machine=self.vm, name="wg-airvpn1")
        self.assertIsNone(t.device)
        self.assertEqual(t.host, self.vm)
        self.assertEqual(str(t), f"{self.vm}: wg-airvpn1")
        t.full_clean()

    def test_device_host(self):
        t = WireGuardTunnel.objects.create(device=self.device, name="tun_wg0")
        self.assertEqual(t.host, self.device)

    def test_clean_rejects_no_host(self):
        with self.assertRaises(ValidationError):
            WireGuardTunnel(name="orphan").full_clean()

    def test_clean_rejects_both_hosts(self):
        with self.assertRaises(ValidationError):
            WireGuardTunnel(device=self.device, virtual_machine=self.vm, name="both").full_clean()

    def test_db_rejects_no_host(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            WireGuardTunnel.objects.create(name="orphan")

    def test_db_rejects_both_hosts(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            WireGuardTunnel.objects.create(device=self.device, virtual_machine=self.vm, name="both")

    def test_unique_vm_name(self):
        WireGuardTunnel.objects.create(virtual_machine=self.vm, name="wg-airvpn1")
        with self.assertRaises(IntegrityError), transaction.atomic():
            WireGuardTunnel.objects.create(virtual_machine=self.vm, name="wg-airvpn1")

    def test_same_name_on_device_and_vm_allowed(self):
        WireGuardTunnel.objects.create(device=self.device, name="wg0")
        t = WireGuardTunnel.objects.create(virtual_machine=self.vm, name="wg0")
        self.assertEqual(t.host, self.vm)

    def test_cascade_delete_with_vm(self):
        WireGuardTunnel.objects.create(virtual_machine=self.vm, name="wg-airvpn1")
        self.vm.delete()
        self.assertEqual(WireGuardTunnel.objects.count(), 0)


class WireGuardPeerModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.device = create_test_device("fw1")
        cls.tunnel = WireGuardTunnel.objects.create(
            device=cls.device, name="tun_wg0", listen_port=51820, address="172.20.20.254/24",
        )

    def test_create_str_and_url(self):
        p = WireGuardPeer.objects.create(
            tunnel=self.tunnel, name="JamesGrieveDesktop", public_key="pk1",
            allowed_ips="172.20.20.1/32", endpoint="desktop.example.com", endpoint_port=51820,
        )
        self.assertEqual(str(p), f"{self.tunnel}: JamesGrieveDesktop")
        self.assertIn("/plugins/wireguard/peers/", p.get_absolute_url())

    def test_defaults_and_roadwarrior_blank_endpoint(self):
        p = WireGuardPeer.objects.create(tunnel=self.tunnel, name="phone", public_key="pk2")
        self.assertTrue(p.enabled)
        self.assertFalse(p.has_preshared_key)
        self.assertEqual(p.endpoint, "")
        self.assertIsNone(p.endpoint_port)
        self.assertIsNone(p.persistent_keepalive)
        self.assertEqual(p.allowed_ips, "")

    def test_multi_value_allowed_ips_roundtrip(self):
        p = WireGuardPeer.objects.create(
            tunnel=self.tunnel, name="site", public_key="pk3",
            allowed_ips="10.0.0.0/24\n192.168.50.0/24",
        )
        p.refresh_from_db()
        self.assertEqual(p.allowed_ips, "10.0.0.0/24\n192.168.50.0/24")

    def test_has_preshared_key_flag_only(self):
        p = WireGuardPeer.objects.create(
            tunnel=self.tunnel, name="psk-peer", public_key="pk4", has_preshared_key=True,
        )
        self.assertTrue(p.has_preshared_key)
        field_names = {f.name for f in WireGuardPeer._meta.get_fields()}
        self.assertNotIn("preshared_key", field_names)

    def test_unique_tunnel_name(self):
        WireGuardPeer.objects.create(tunnel=self.tunnel, name="dup", public_key="pkA")
        with self.assertRaises(IntegrityError), transaction.atomic():
            WireGuardPeer.objects.create(tunnel=self.tunnel, name="dup", public_key="pkB")

    def test_failover_priority_defaults_blank(self):
        p = WireGuardPeer.objects.create(tunnel=self.tunnel, name="always-on", public_key="pk6")
        self.assertIsNone(p.failover_priority)

    def test_failover_priority_unique_per_tunnel(self):
        WireGuardPeer.objects.create(tunnel=self.tunnel, name="srv-a", public_key="pk7", failover_priority=1)
        with self.assertRaises(IntegrityError), transaction.atomic():
            WireGuardPeer.objects.create(tunnel=self.tunnel, name="srv-b", public_key="pk7", failover_priority=1)

    def test_failover_priority_blank_not_unique(self):
        WireGuardPeer.objects.create(tunnel=self.tunnel, name="n1", public_key="pk8")
        WireGuardPeer.objects.create(tunnel=self.tunnel, name="n2", public_key="pk9")
        self.assertEqual(self.tunnel.peers.filter(failover_priority__isnull=True).count(), 2)

    def test_failover_priority_orders_peers(self):
        WireGuardPeer.objects.create(tunnel=self.tunnel, name="a-second", public_key="pkS", failover_priority=2)
        WireGuardPeer.objects.create(tunnel=self.tunnel, name="z-first", public_key="pkS", failover_priority=1)
        self.assertEqual([p.name for p in self.tunnel.peers.all()], ["z-first", "a-second"])

    def test_cascade_delete_with_tunnel(self):
        WireGuardPeer.objects.create(tunnel=self.tunnel, name="p1", public_key="pk5")
        self.assertEqual(self.tunnel.peers.count(), 1)
        self.tunnel.delete()
        self.assertEqual(WireGuardPeer.objects.count(), 0)

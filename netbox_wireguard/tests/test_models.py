# SPDX-License-Identifier: AGPL-3.0-or-later
"""Model tests against a real DB (no mocks): creation, str, constraints, FK behaviour."""
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError
from django.test import TestCase
from utilities.testing import create_test_device
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

    def test_assign_interface_requires_name_and_instance(self):
        t = WireGuardTunnel(device=self.device, name="tun_wg0", assign_interface=True)
        with self.assertRaises(ValidationError) as ctx:
            t.full_clean()
        self.assertIn("interface_name", ctx.exception.message_dict)
        self.assertIn("wg_instance", ctx.exception.message_dict)


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

    def test_cascade_delete_with_tunnel(self):
        WireGuardPeer.objects.create(tunnel=self.tunnel, name="p1", public_key="pk5")
        self.assertEqual(self.tunnel.peers.count(), 1)
        self.tunnel.delete()
        self.assertEqual(WireGuardPeer.objects.count(), 0)

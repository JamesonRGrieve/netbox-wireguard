# SPDX-License-Identifier: AGPL-3.0-or-later
"""Native WireGuard topology model — the **non-secret** half only.

Tunnel private keys and per-peer pre-shared keys live in OpenBao, never here. Each
non-secret WireGuard field is a real column → a zero-loss SoT for the intended topology,
which the ansible-tofu reconcilers read back 1:1.
"""
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel


class WireGuardTunnel(NetBoxModel):
    """A WireGuard tunnel interface on a device (e.g. OPNsense ``tun_wg0``).

    Holds the non-secret tunnel shape: listen port, interface CIDR, the tunnel's own
    public key, MTU. The private key lives in OpenBao, NOT here.
    """
    device = models.ForeignKey(
        "dcim.Device", on_delete=models.CASCADE, related_name="wg_tunnels"
    )
    name = models.CharField(max_length=64, help_text="Tunnel/interface name (e.g. tun_wg0).")
    listen_port = models.PositiveIntegerField(null=True, blank=True)
    address = models.CharField(
        max_length=64, blank=True,
        help_text="Tunnel interface CIDR (e.g. 172.20.20.254/24); blank if none.",
    )
    public_key = models.CharField(
        max_length=128, blank=True,
        help_text="Tunnel public key (NON-secret; the private key lives in OpenBao).",
    )
    mtu = models.PositiveIntegerField(null=True, blank=True)
    description = models.CharField(max_length=200, blank=True)
    enabled = models.BooleanField(default=True)
    assign_interface = models.BooleanField(
        default=False,
        help_text="Assign this tunnel as an OPNsense/pfSense interface (optN) so firewall/NAT rules can target it by name.",
    )
    interface_name = models.CharField(
        max_length=64, blank=True,
        help_text="Interface description when assigned (e.g. WG_RW); the stable name rules reference. Required when assign_interface is set.",
    )
    wg_instance = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text="WireGuard instance number → interface device wg<instance> (e.g. 0 → wg0). Required when assign_interface is set.",
    )

    class Meta:
        ordering = ["device", "name"]
        verbose_name = "WireGuard Tunnel"
        constraints = [
            models.UniqueConstraint(
                fields=["device", "name"], name="netbox_wireguard_tunnel_device_name"
            ),
        ]

    def clean(self):
        super().clean()
        if self.assign_interface:
            missing = [f for f in ("interface_name", "wg_instance") if not getattr(self, f) and getattr(self, f) != 0]
            if missing:
                raise ValidationError({f: "Required when assign_interface is set." for f in missing})

    def __str__(self):
        return f"{self.device}: {self.name}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_wireguard:wireguardtunnel", args=[self.pk])


class WireGuardPeer(NetBoxModel):
    """A peer of a :class:`WireGuardTunnel` — the non-secret peer shape.

    Holds the peer's public key, endpoint, allowed-IPs, and keepalive. The pre-shared
    key (if any) lives in OpenBao; ``has_preshared_key`` is a flag only — it records
    *that* a PSK exists so reconcilers know to fetch one, never the value itself.
    """
    tunnel = models.ForeignKey(
        WireGuardTunnel, on_delete=models.CASCADE, related_name="peers"
    )
    name = models.CharField(max_length=128, help_text="Peer description (e.g. JamesGrieveDesktop).")
    public_key = models.CharField(max_length=128)
    endpoint = models.CharField(
        max_length=255, blank=True,
        help_text="Peer endpoint host/FQDN; blank for roadwarrior peers with no fixed endpoint.",
    )
    endpoint_port = models.PositiveIntegerField(null=True, blank=True)
    allowed_ips = models.TextField(
        blank=True,
        help_text="Allowed CIDRs, one per line or comma-separated.",
    )
    persistent_keepalive = models.PositiveIntegerField(null=True, blank=True)
    has_preshared_key = models.BooleanField(
        default=False,
        help_text="Flag only: a PSK exists for this peer (the value lives in OpenBao, NOT here).",
    )
    description = models.CharField(max_length=200, blank=True)
    enabled = models.BooleanField(default=True)

    class Meta:
        ordering = ["tunnel", "name"]
        verbose_name = "WireGuard Peer"
        constraints = [
            models.UniqueConstraint(
                fields=["tunnel", "name"], name="netbox_wireguard_peer_tunnel_name"
            ),
        ]

    def __str__(self):
        return f"{self.tunnel}: {self.name}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_wireguard:wireguardpeer", args=[self.pk])

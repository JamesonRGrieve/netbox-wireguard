# SPDX-License-Identifier: AGPL-3.0-or-later
from dcim.models import Device
from django import forms
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm
from utilities.forms.fields import DynamicModelChoiceField, DynamicModelMultipleChoiceField, TagFilterField
from utilities.forms.rendering import FieldSet
from .models import WireGuardPeer, WireGuardTunnel


class WireGuardTunnelForm(NetBoxModelForm):
    device = DynamicModelChoiceField(queryset=Device.objects.all())

    fieldsets = (
        FieldSet("device", "name", "enabled", name="Tunnel"),
        FieldSet("listen_port", "address", "mtu", name="Interface"),
        FieldSet("assign_interface", "interface_name", "wg_instance", name="Interface assignment"),
        FieldSet("public_key", name="Key (non-secret)"),
        FieldSet("description", "tags", name="Misc"),
    )

    class Meta:
        model = WireGuardTunnel
        fields = [
            "device", "name", "listen_port", "address", "public_key", "mtu",
            "assign_interface", "interface_name", "wg_instance",
            "description", "enabled", "tags",
        ]


class WireGuardPeerForm(NetBoxModelForm):
    tunnel = DynamicModelChoiceField(queryset=WireGuardTunnel.objects.all())

    fieldsets = (
        FieldSet("tunnel", "name", "enabled", name="Peer"),
        FieldSet("public_key", "has_preshared_key", name="Keys (non-secret)"),
        FieldSet("endpoint", "endpoint_port", "allowed_ips", "persistent_keepalive", name="Connection"),
        FieldSet("description", "tags", name="Misc"),
    )

    class Meta:
        model = WireGuardPeer
        fields = [
            "tunnel", "name", "public_key", "endpoint", "endpoint_port", "allowed_ips",
            "persistent_keepalive", "has_preshared_key", "description", "enabled", "tags",
        ]


class WireGuardTunnelFilterForm(NetBoxModelFilterSetForm):
    model = WireGuardTunnel
    device_id = DynamicModelMultipleChoiceField(queryset=Device.objects.all(), required=False, label="Device")
    enabled = forms.NullBooleanField(required=False)
    tag = TagFilterField(WireGuardTunnel)


class WireGuardPeerFilterForm(NetBoxModelFilterSetForm):
    model = WireGuardPeer
    tunnel_id = DynamicModelMultipleChoiceField(queryset=WireGuardTunnel.objects.all(), required=False, label="Tunnel")
    has_preshared_key = forms.NullBooleanField(required=False)
    enabled = forms.NullBooleanField(required=False)
    tag = TagFilterField(WireGuardPeer)

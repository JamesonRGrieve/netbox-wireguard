# SPDX-License-Identifier: AGPL-3.0-or-later
import django_filters
from dcim.models import Device
from django.db.models import Q
from netbox.filtersets import NetBoxModelFilterSet
from .models import WireGuardPeer, WireGuardTunnel


class WireGuardTunnelFilterSet(NetBoxModelFilterSet):
    # Explicit FK filters: django-filter does NOT derive `<fk>_id` from a bare FK in
    # Meta.fields, so `?device_id=` would be silently ignored. NetBox convention is
    # `<fk>_id` (by PK) + `<fk>` (by natural key).
    device_id = django_filters.ModelMultipleChoiceFilter(
        field_name="device", queryset=Device.objects.all(), label="Device (ID)",
    )
    device = django_filters.ModelMultipleChoiceFilter(
        field_name="device__name", to_field_name="name", queryset=Device.objects.all(),
        label="Device (name)",
    )

    class Meta:
        model = WireGuardTunnel
        fields = ["id", "name", "listen_port", "address", "public_key", "mtu", "enabled"]

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | Q(address__icontains=value) | Q(description__icontains=value)
        )


class WireGuardPeerFilterSet(NetBoxModelFilterSet):
    tunnel_id = django_filters.ModelMultipleChoiceFilter(
        field_name="tunnel", queryset=WireGuardTunnel.objects.all(), label="Tunnel (ID)",
    )
    tunnel = django_filters.ModelMultipleChoiceFilter(
        field_name="tunnel__name", to_field_name="name", queryset=WireGuardTunnel.objects.all(),
        label="Tunnel (name)",
    )

    class Meta:
        model = WireGuardPeer
        fields = [
            "id", "name", "public_key", "endpoint", "endpoint_port",
            "persistent_keepalive", "has_preshared_key", "enabled",
        ]

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | Q(public_key__icontains=value)
            | Q(endpoint__icontains=value) | Q(allowed_ips__icontains=value)
            | Q(description__icontains=value)
        )

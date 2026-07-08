# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.api.viewsets import NetBoxModelViewSet
from .. import filtersets
from ..models import WireGuardPeer, WireGuardTunnel
from .serializers import WireGuardPeerSerializer, WireGuardTunnelSerializer


class WireGuardTunnelViewSet(NetBoxModelViewSet):
    queryset = WireGuardTunnel.objects.prefetch_related("device", "tags")
    serializer_class = WireGuardTunnelSerializer
    filterset_class = filtersets.WireGuardTunnelFilterSet


class WireGuardPeerViewSet(NetBoxModelViewSet):
    queryset = WireGuardPeer.objects.prefetch_related("tunnel", "tags")
    serializer_class = WireGuardPeerSerializer
    filterset_class = filtersets.WireGuardPeerFilterSet

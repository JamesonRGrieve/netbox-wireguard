# SPDX-License-Identifier: AGPL-3.0-or-later
from typing import Annotated, List

import strawberry
import strawberry_django
from netbox.graphql.types import NetBoxObjectType

from ..models import WireGuardPeer, WireGuardTunnel
from .filters import WireGuardPeerFilter, WireGuardTunnelFilter


@strawberry_django.type(WireGuardTunnel, fields="__all__", filters=WireGuardTunnelFilter, pagination=True)
class WireGuardTunnelType(NetBoxObjectType):
    name: str
    device: Annotated["DeviceType", strawberry.lazy("dcim.graphql.types")]
    peers: List[Annotated["WireGuardPeerType", strawberry.lazy("netbox_wireguard.graphql.types")]]


@strawberry_django.type(WireGuardPeer, fields="__all__", filters=WireGuardPeerFilter, pagination=True)
class WireGuardPeerType(NetBoxObjectType):
    name: str
    public_key: str
    tunnel: Annotated["WireGuardTunnelType", strawberry.lazy("netbox_wireguard.graphql.types")]

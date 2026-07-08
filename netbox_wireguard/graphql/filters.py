# SPDX-License-Identifier: AGPL-3.0-or-later
from typing import Annotated, TYPE_CHECKING

import strawberry
import strawberry_django
from netbox.graphql.filters import NetBoxModelFilter
from strawberry_django import StrFilterLookup

from ..models import WireGuardPeer, WireGuardTunnel

if TYPE_CHECKING:
    pass

__all__ = ("WireGuardTunnelFilter", "WireGuardPeerFilter")


@strawberry_django.filter_type(WireGuardTunnel, lookups=True)
class WireGuardTunnelFilter(NetBoxModelFilter):
    name: StrFilterLookup[str] | None = strawberry_django.filter_field()
    peers: (
        Annotated["WireGuardPeerFilter", strawberry.lazy("netbox_wireguard.graphql.filters")] | None
    ) = strawberry_django.filter_field()


@strawberry_django.filter_type(WireGuardPeer, lookups=True)
class WireGuardPeerFilter(NetBoxModelFilter):
    name: StrFilterLookup[str] | None = strawberry_django.filter_field()
    tunnel: (
        Annotated["WireGuardTunnelFilter", strawberry.lazy("netbox_wireguard.graphql.filters")] | None
    ) = strawberry_django.filter_field()

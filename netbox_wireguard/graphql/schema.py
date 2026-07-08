# SPDX-License-Identifier: AGPL-3.0-or-later
from typing import List

import strawberry
import strawberry_django

from .types import WireGuardPeerType, WireGuardTunnelType


@strawberry.type(name="Query")
class WireGuardTunnelQuery:
    netbox_wireguard_tunnel: WireGuardTunnelType = strawberry_django.field()
    netbox_wireguard_tunnel_list: List[WireGuardTunnelType] = strawberry_django.field()


@strawberry.type(name="Query")
class WireGuardPeerQuery:
    netbox_wireguard_peer: WireGuardPeerType = strawberry_django.field()
    netbox_wireguard_peer_list: List[WireGuardPeerType] = strawberry_django.field()

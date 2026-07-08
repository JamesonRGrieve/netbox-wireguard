# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.api.routers import NetBoxRouter
from . import views

app_name = "netbox_wireguard"

router = NetBoxRouter()
router.register("tunnels", views.WireGuardTunnelViewSet)
router.register("peers", views.WireGuardPeerViewSet)

urlpatterns = router.urls

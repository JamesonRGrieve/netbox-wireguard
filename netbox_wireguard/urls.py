# SPDX-License-Identifier: AGPL-3.0-or-later
from django.urls import path
from netbox.views.generic import ObjectChangeLogView, ObjectJournalView
from . import models, views

urlpatterns = [
    # Tunnels
    path("tunnels/", views.WireGuardTunnelListView.as_view(), name="wireguardtunnel_list"),
    path("tunnels/add/", views.WireGuardTunnelEditView.as_view(), name="wireguardtunnel_add"),
    path("tunnels/delete/", views.WireGuardTunnelBulkDeleteView.as_view(), name="wireguardtunnel_bulk_delete"),
    path("tunnels/<int:pk>/", views.WireGuardTunnelView.as_view(), name="wireguardtunnel"),
    path("tunnels/<int:pk>/edit/", views.WireGuardTunnelEditView.as_view(), name="wireguardtunnel_edit"),
    path("tunnels/<int:pk>/delete/", views.WireGuardTunnelDeleteView.as_view(), name="wireguardtunnel_delete"),
    path("tunnels/<int:pk>/changelog/", ObjectChangeLogView.as_view(), name="wireguardtunnel_changelog", kwargs={"model": models.WireGuardTunnel}),
    path("tunnels/<int:pk>/journal/", ObjectJournalView.as_view(), name="wireguardtunnel_journal", kwargs={"model": models.WireGuardTunnel}),
    # Peers
    path("peers/", views.WireGuardPeerListView.as_view(), name="wireguardpeer_list"),
    path("peers/add/", views.WireGuardPeerEditView.as_view(), name="wireguardpeer_add"),
    path("peers/delete/", views.WireGuardPeerBulkDeleteView.as_view(), name="wireguardpeer_bulk_delete"),
    path("peers/<int:pk>/", views.WireGuardPeerView.as_view(), name="wireguardpeer"),
    path("peers/<int:pk>/edit/", views.WireGuardPeerEditView.as_view(), name="wireguardpeer_edit"),
    path("peers/<int:pk>/delete/", views.WireGuardPeerDeleteView.as_view(), name="wireguardpeer_delete"),
    path("peers/<int:pk>/changelog/", ObjectChangeLogView.as_view(), name="wireguardpeer_changelog", kwargs={"model": models.WireGuardPeer}),
    path("peers/<int:pk>/journal/", ObjectJournalView.as_view(), name="wireguardpeer_journal", kwargs={"model": models.WireGuardPeer}),
]

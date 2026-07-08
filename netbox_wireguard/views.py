# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.views import generic
from . import filtersets, forms, models, tables


class WireGuardTunnelView(generic.ObjectView):
    queryset = models.WireGuardTunnel.objects.all()


class WireGuardTunnelListView(generic.ObjectListView):
    queryset = models.WireGuardTunnel.objects.all()
    table = tables.WireGuardTunnelTable
    filterset = filtersets.WireGuardTunnelFilterSet
    filterset_form = forms.WireGuardTunnelFilterForm


class WireGuardTunnelEditView(generic.ObjectEditView):
    queryset = models.WireGuardTunnel.objects.all()
    form = forms.WireGuardTunnelForm


class WireGuardTunnelDeleteView(generic.ObjectDeleteView):
    queryset = models.WireGuardTunnel.objects.all()


class WireGuardTunnelBulkDeleteView(generic.BulkDeleteView):
    queryset = models.WireGuardTunnel.objects.all()
    table = tables.WireGuardTunnelTable


class WireGuardPeerView(generic.ObjectView):
    queryset = models.WireGuardPeer.objects.all()


class WireGuardPeerListView(generic.ObjectListView):
    queryset = models.WireGuardPeer.objects.all()
    table = tables.WireGuardPeerTable
    filterset = filtersets.WireGuardPeerFilterSet
    filterset_form = forms.WireGuardPeerFilterForm


class WireGuardPeerEditView(generic.ObjectEditView):
    queryset = models.WireGuardPeer.objects.all()
    form = forms.WireGuardPeerForm


class WireGuardPeerDeleteView(generic.ObjectDeleteView):
    queryset = models.WireGuardPeer.objects.all()


class WireGuardPeerBulkDeleteView(generic.BulkDeleteView):
    queryset = models.WireGuardPeer.objects.all()
    table = tables.WireGuardPeerTable

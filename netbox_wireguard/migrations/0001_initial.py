# SPDX-License-Identifier: AGPL-3.0-or-later
# Hand-authored initial migration (NetBox disables makemigrations in production).
# Verify against the target NetBox before deploy:
#   python manage.py makemigrations netbox_wireguard --check --dry-run
import django.db.models.deletion
import taggit.managers
import utilities.json
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("dcim", "0001_initial"),
        ("extras", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="WireGuardTunnel",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, blank=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, blank=True, null=True)),
                ("custom_field_data", models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ("name", models.CharField(max_length=64)),
                ("listen_port", models.PositiveIntegerField(blank=True, null=True)),
                ("address", models.CharField(blank=True, max_length=64)),
                ("public_key", models.CharField(blank=True, max_length=128)),
                ("mtu", models.PositiveIntegerField(blank=True, null=True)),
                ("description", models.CharField(blank=True, max_length=200)),
                ("enabled", models.BooleanField(default=True)),
                ("device", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="wg_tunnels", to="dcim.device")),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={"verbose_name": "WireGuard Tunnel", "ordering": ["device", "name"]},
        ),
        migrations.CreateModel(
            name="WireGuardPeer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, blank=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, blank=True, null=True)),
                ("custom_field_data", models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ("name", models.CharField(max_length=128)),
                ("public_key", models.CharField(max_length=128)),
                ("endpoint", models.CharField(blank=True, max_length=255)),
                ("endpoint_port", models.PositiveIntegerField(blank=True, null=True)),
                ("allowed_ips", models.TextField(blank=True)),
                ("persistent_keepalive", models.PositiveIntegerField(blank=True, null=True)),
                ("has_preshared_key", models.BooleanField(default=False)),
                ("description", models.CharField(blank=True, max_length=200)),
                ("enabled", models.BooleanField(default=True)),
                ("tunnel", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="peers", to="netbox_wireguard.wireguardtunnel")),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={"verbose_name": "WireGuard Peer", "ordering": ["tunnel", "name"]},
        ),
        migrations.AddConstraint(
            model_name="wireguardtunnel",
            constraint=models.UniqueConstraint(fields=("device", "name"), name="netbox_wireguard_tunnel_device_name"),
        ),
        migrations.AddConstraint(
            model_name="wireguardpeer",
            constraint=models.UniqueConstraint(fields=("tunnel", "name"), name="netbox_wireguard_peer_tunnel_name"),
        ),
    ]

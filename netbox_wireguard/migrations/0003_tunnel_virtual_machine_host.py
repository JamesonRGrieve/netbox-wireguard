# SPDX-License-Identifier: AGPL-3.0-or-later
# Hand-authored migration (NetBox disables makemigrations in production).
# Verify against the target NetBox before deploy:
#   python manage.py makemigrations netbox_wireguard --check --dry-run
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_wireguard", "0002_tunnel_interface_assignment"),
        ("virtualization", "0001_squashed_0022"),
    ]
    operations = [
        migrations.AlterField(
            model_name="wireguardtunnel",
            name="device",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                related_name="wg_tunnels", to="dcim.device",
            ),
        ),
        migrations.AddField(
            model_name="wireguardtunnel",
            name="virtual_machine",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                related_name="wg_tunnels", to="virtualization.virtualmachine",
            ),
        ),
        migrations.AddField(
            model_name="wireguardtunnel",
            name="dns",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterModelOptions(
            name="wireguardtunnel",
            options={
                "ordering": ["device", "virtual_machine", "name"],
                "verbose_name": "WireGuard Tunnel",
            },
        ),
        migrations.AddConstraint(
            model_name="wireguardtunnel",
            constraint=models.UniqueConstraint(
                fields=("virtual_machine", "name"), name="netbox_wireguard_tunnel_vm_name"
            ),
        ),
        migrations.AddConstraint(
            model_name="wireguardtunnel",
            constraint=models.CheckConstraint(
                condition=models.Q(("device__isnull", False), ("virtual_machine__isnull", True))
                | models.Q(("device__isnull", True), ("virtual_machine__isnull", False)),
                name="netbox_wireguard_tunnel_one_host",
            ),
        ),
    ]

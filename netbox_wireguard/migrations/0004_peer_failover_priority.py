# SPDX-License-Identifier: AGPL-3.0-or-later
# Hand-authored migration (NetBox disables makemigrations in production).
# Verify against the target NetBox before deploy:
#   python manage.py makemigrations netbox_wireguard --check --dry-run
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_wireguard", "0003_tunnel_virtual_machine_host"),
    ]
    operations = [
        migrations.AddField(
            model_name="wireguardpeer",
            name="failover_priority",
            field=models.PositiveSmallIntegerField(
                blank=True, null=True,
                help_text=(
                    "Failover order among this tunnel's alternative peers (lowest = preferred). "
                    "Peers carrying a priority are mutually exclusive: the host runs one at a time "
                    "and moves to the next when the active one stops handshaking. Blank = always-on peer."
                ),
            ),
        ),
        migrations.AlterModelOptions(
            name="wireguardpeer",
            options={
                "ordering": ["tunnel", "failover_priority", "name"],
                "verbose_name": "WireGuard Peer",
            },
        ),
        migrations.AddConstraint(
            model_name="wireguardpeer",
            constraint=models.UniqueConstraint(
                condition=models.Q(("failover_priority__isnull", False)),
                fields=("tunnel", "failover_priority"),
                name="netbox_wireguard_peer_tunnel_failover_priority",
            ),
        ),
    ]

# SPDX-License-Identifier: AGPL-3.0-or-later
# Hand-authored migration (NetBox disables makemigrations in production).
# Verify against the target NetBox before deploy:
#   python manage.py makemigrations netbox_wireguard --check --dry-run
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_wireguard", "0001_initial"),
    ]
    operations = [
        migrations.AddField(
            model_name="wireguardtunnel",
            name="assign_interface",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="wireguardtunnel",
            name="interface_name",
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name="wireguardtunnel",
            name="wg_instance",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]

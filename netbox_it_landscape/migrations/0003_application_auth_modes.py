# Generated for digital health authentication indicator PROC-09A
# (HospiConnect / HOP'EN 2). Additive schema change, no data required.

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_it_landscape', '0002_remove_application_netbox_it_landscape_application_unique_process_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='authentication_modes',
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=30),
                blank=True, null=True, size=None,
                help_text='Authentication modes available for this service (PROC-09A).',
                verbose_name='Authentication modes',
            ),
        ),
        migrations.AddField(
            model_name='application',
            name='authentication_primary',
            field=models.CharField(blank=True, max_length=30, verbose_name='Primary authentication mode'),
        ),
        migrations.AddField(
            model_name='application',
            name='authentication_maintained',
            field=models.BooleanField(
                default=False,
                help_text='A maintenance rule keeps the mapping applicable (PROC-09A).',
                verbose_name='Authentication mapping maintained',
            ),
        ),
        migrations.AddField(
            model_name='application',
            name='authentication_notes',
            field=models.CharField(
                blank=True, max_length=200,
                help_text='Maintenance rule / reference identity provider.',
                verbose_name='Authentication notes',
            ),
        ),
    ]

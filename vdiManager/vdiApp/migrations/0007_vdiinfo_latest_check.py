# Generated by Django 3.2.19 on 2023-12-20 05:47

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('vdiApp', '0006_vdiinfo_api_enabled'),
    ]

    operations = [
        migrations.AddField(
            model_name='vdiinfo',
            name='latest_check',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='آخرین چک'),
            preserve_default=False,
        ),
    ]

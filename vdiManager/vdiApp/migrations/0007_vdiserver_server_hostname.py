# Generated by Django 3.2.19 on 2023-08-17 06:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vdiApp', '0006_auto_20230817_0420'),
    ]

    operations = [
        migrations.AddField(
            model_name='vdiserver',
            name='server_hostname',
            field=models.CharField(blank=True, max_length=25, verbose_name='دامنه سرور'),
        ),
    ]

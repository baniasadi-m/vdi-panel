# Generated by Django 3.2.19 on 2023-11-29 09:05

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('vdiApp', '0004_vdiinfo_company_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='vdiinfo',
            name='company_short_name',
            field=models.CharField(default=django.utils.timezone.now, max_length=100, verbose_name='نام کوتاه سازمان'),
            preserve_default=False,
        ),
    ]

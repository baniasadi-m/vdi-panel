# Generated by Django 3.2.19 on 2023-07-03 08:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vdiApp', '0003_virtualdesktop_vd_browser_img'),
    ]

    operations = [
        migrations.AlterField(
            model_name='virtualdesktop',
            name='vd_container_name',
            field=models.CharField(blank=True, max_length=100, verbose_name='نام میزکار'),
        ),
        migrations.AlterField(
            model_name='virtualdesktop',
            name='vd_container_password',
            field=models.CharField(blank=True, max_length=25, verbose_name=' پسورد میزکار'),
        ),
        migrations.AlterField(
            model_name='virtualdesktop',
            name='vd_container_user',
            field=models.CharField(blank=True, max_length=25, verbose_name=' کاربری میزکار'),
        ),
    ]

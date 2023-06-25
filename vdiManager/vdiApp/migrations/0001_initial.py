# Generated by Django 3.2 on 2023-06-25 11:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='VDIServer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vd_server_name', models.CharField(blank=True, max_length=255, verbose_name='دارنده میزکار')),
                ('vd_server_ip', models.CharField(blank=True, max_length=25, verbose_name='آدرس سرور')),
                ('description', models.TextField(blank=True, verbose_name='توضیحات ')),
                ('is_enabled', models.BooleanField(default=True, verbose_name='فعال')),
            ],
            options={
                'verbose_name': ' سرور ',
                'verbose_name_plural': 'سرور ها',
            },
        ),
        migrations.CreateModel(
            name='VirtualDesktop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vd_container_name', models.CharField(blank=True, max_length=100, verbose_name='نام کانتینر')),
                ('vd_container_cpu', models.CharField(blank=True, max_length=25, verbose_name='مقدار پردازنده')),
                ('vd_container_mem', models.CharField(blank=True, max_length=25, verbose_name='مقدار حافظه')),
                ('vd_container_img', models.CharField(blank=True, max_length=25, verbose_name=' ایمیج')),
                ('vd_container_id', models.CharField(blank=True, max_length=25, verbose_name=' شناسه کانتینر')),
                ('vd_owner', models.CharField(blank=True, max_length=255, verbose_name='نام تحویل گیرنده')),
                ('vd_letter_number', models.IntegerField(blank=True, default=1111, verbose_name='شماره نامه')),
                ('vd_description', models.TextField(blank=True, verbose_name='توضیحات')),
                ('vd_creator_ip', models.TextField(blank=True, verbose_name=' آیپی کاربر')),
                ('vd_is_activate', models.BooleanField(default=True, verbose_name='فعال')),
                ('vd_created_by', models.CharField(blank=True, max_length=255, verbose_name='ایجاد کننده')),
                ('vd_created_at', models.DateTimeField(verbose_name='تاریخ ایجاد')),
                ('vd_revoked_at', models.DateTimeField(auto_now=True, verbose_name='تاریخ ابطال')),
                ('vd_expired_at', models.DateTimeField(verbose_name='تاریخ انقضا')),
                ('vd_server', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='vdiApp.vdiserver', verbose_name='سرور')),
            ],
            options={
                'verbose_name': ' میزکار ',
                'verbose_name_plural': 'میزکار ها',
            },
        ),
    ]

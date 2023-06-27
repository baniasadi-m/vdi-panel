from faulthandler import is_enabled
from tabnanny import verbose
from django.db import models
from django.forms import ModelForm
import datetime,os
from django.conf import settings
# Create your models here.

class VDIServer(models.Model):
    class Meta:
        verbose_name=" سرور "
        verbose_name_plural ="سرور ها"
    data_path = models.CharField(blank=True, max_length=255,verbose_name="مسیر داده ها")
    server_name = models.CharField(blank=True, max_length=255,verbose_name="اسم سرور")
    server_ip = models.CharField(blank=True, max_length=25,verbose_name="آدرس سرور")
    server_port = models.CharField(blank=True, max_length=25,verbose_name="پورت سرور")
    server_scheme = models.CharField(blank=True, max_length=25,verbose_name="تنظیم ssl")
    description = models.TextField(blank=True,verbose_name="توضیحات ")
    is_enabled = models.BooleanField(default=True,verbose_name="فعال")

    def __str__(self) :
        return self.server_name

class VirtualDesktop(models.Model):
    class Meta:
        verbose_name=" میزکار "
        verbose_name_plural ="میزکار ها"
    vd_container_name = models.CharField(blank=True, max_length=100,verbose_name="نام میزکار")
    vd_container_cpu = models.CharField(blank=True, max_length=25,verbose_name="مقدار پردازنده")
    vd_container_mem = models.CharField(blank=True, max_length=25,verbose_name="مقدار حافظه")
    vd_container_img = models.CharField(blank=True, max_length=255,verbose_name=" ایمیج")
    vd_container_id = models.CharField(blank=True, max_length=255,verbose_name=" شناسه کانتینر")
    vd_container_shortid = models.CharField(blank=True, max_length=255,verbose_name=" شناسه کوتاه کانتینر")
    vd_container_user = models.CharField(blank=True, max_length=25,verbose_name=" کاربری میزکار")
    vd_container_password = models.CharField(blank=True, max_length=25,verbose_name=" پسورد میزکار")
    vd_container_vncpass = models.CharField(blank=True, max_length=25,verbose_name=" پسوردvnc")
    vd_browser_id = models.CharField(blank=True, max_length=255,verbose_name=" شناسه فایل منیجر")
    vd_browser_img = models.CharField(blank=True, max_length=255,verbose_name=" ایمیج فایل منیجر")
    vd_browser_name = models.CharField(blank=True, max_length=255,verbose_name=" نام فایل منیجر")
    vd_browser_port = models.CharField(blank=True, max_length=255,verbose_name=" پورت فایل منیجر")
    vd_port = models.CharField(blank=True, max_length=25,verbose_name=" پورت میزکار")
    vd_server = models.ForeignKey('VDIServer',on_delete=models.DO_NOTHING,verbose_name="سرور")
    vd_owner = models.CharField(blank=True, max_length=255,verbose_name="نام تحویل گیرنده")
    vd_letter_number = models.IntegerField(blank=True,default=1111,verbose_name="شماره نامه")
    vd_description = models.TextField(blank=True, verbose_name="توضیحات")
    vd_creator_ip = models.CharField(blank=True,max_length=255, verbose_name=" آیپی ایجاد کننده")
    vd_is_activate = models.BooleanField(blank=False,default=True, verbose_name="فعال")
    vd_created_by = models.CharField(blank=True, max_length=255,verbose_name="ایجاد کننده")
    vd_created_at = models.DateTimeField(blank=False,auto_now=True, verbose_name="تاریخ ایجاد")
    vd_revoked_at = models.DateTimeField(blank=False,auto_now=True, verbose_name="تاریخ ابطال")
    vd_expired_at = models.DateTimeField(blank=False,auto_now=True, verbose_name="تاریخ انقضا")

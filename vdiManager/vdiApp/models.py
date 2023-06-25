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
    server_name = models.CharField(blank=True, max_length=255,verbose_name="دارنده میزکار")
    server_ip = models.CharField(blank=True, max_length=25,verbose_name="آدرس سرور")
    description = models.TextField(blank=True,verbose_name="توضیحات ")
    is_enabled = models.BooleanField(default=True,verbose_name="فعال")

    def __str__(self) :
        return self.server_name

class VirtualDesktop(models.Model):
    class Meta:
        verbose_name=" میزکار "
        verbose_name_plural ="میزکار ها"
    vd_container_name = models.CharField(blank=True, max_length=100,verbose_name="نام کانتینر")
    vd_container_cpu = models.CharField(blank=True, max_length=25,verbose_name="مقدار پردازنده")
    vd_container_mem = models.CharField(blank=True, max_length=25,verbose_name="مقدار حافظه")
    vd_container_img = models.CharField(blank=True, max_length=25,verbose_name=" ایمیج")
    vd_container_id = models.CharField(blank=True, max_length=25,verbose_name=" شناسه کانتینر")
    vd_server = models.ForeignKey('VDIServer',on_delete=models.DO_NOTHING,verbose_name="سرور")
    vd_owner = models.CharField(blank=True, max_length=255,verbose_name="نام تحویل گیرنده")
    vd_letter_number = models.IntegerField(blank=True,default=1111,verbose_name="شماره نامه")
    vd_description = models.TextField(blank=True, verbose_name="توضیحات")
    vd_creator_ip = models.CharField(blank=True,max_length=255, verbose_name=" آیپی کاربر")
    vd_is_activate = models.BooleanField(blank=False,default=True, verbose_name="فعال")
    vd_created_by = models.CharField(blank=True, max_length=255,verbose_name="ایجاد کننده")
    vd_created_at = models.DateTimeField(blank=False, verbose_name="تاریخ ایجاد")
    vd_revoked_at = models.DateTimeField(blank=False,auto_now=True ,verbose_name="تاریخ ابطال")
    vd_expired_at = models.DateTimeField(blank=False, verbose_name="تاریخ انقضا")

from django.db import models
from django.core.validators import validate_ipv4_address
from django.conf import settings
from vdiManager.settings import Config
# Create your models here.

def get_expiry_time():
    from datetime import datetime,timedelta
    return datetime.now() + timedelta(days=int(Config.VDI_EXPIRY_DAYS))

class VDIServer(models.Model):
    class Meta:
        verbose_name=" سرور "
        verbose_name_plural ="سرور ها"
    data_path = models.CharField(blank=True, max_length=255,verbose_name="مسیر داده ها")
    server_name = models.CharField(blank=True, max_length=255,verbose_name="اسم سرور")
    server_ip = models.CharField(blank=True, max_length=25,verbose_name="آدرس سرور")
    server_port = models.CharField(blank=True, max_length=25,verbose_name="پورت سرور")
    server_scheme = models.CharField(blank=True, max_length=25,verbose_name="تنظیم ssl")
    server_hostname = models.CharField(blank=True, max_length=25,verbose_name="دامنه سرور")
    description = models.TextField(blank=True,verbose_name="توضیحات ")
    is_enabled = models.BooleanField(default=True,verbose_name="فعال")

    def __str__(self) :
        return self.server_name
class UserProfile(models.Model):
    class Meta:
        verbose_name = "پروفایل"
        verbose_name_plural = "پروفایلها"
    owner_name = models.CharField(blank=True, max_length=100,verbose_name="نام تحویل گیرنده")
    owner_user = models.CharField(blank=False, max_length=100,unique=True,verbose_name="کاربری")
    owner_password = models.CharField(blank=False, max_length=100,unique=True,verbose_name="پسورد")
    owner_ip = models.CharField(blank=False,default='1.1.1.1', max_length=100,verbose_name="آیپی کانتینر",validators=[validate_ipv4_address])
    owner_browser_ip = models.CharField(blank=False,default='1.1.1.1', max_length=100,verbose_name="آیپی فایل منیجر",validators=[validate_ipv4_address])
    owner_vd_created_number = models.IntegerField(blank=False, default=0, verbose_name="تعداد ساخته شده")
    owner_description = models.TextField(blank=True, verbose_name="توضیحات")
    owner_create_by_ldap = models.BooleanField(blank=True, verbose_name="LDAP")
    owner_is_active = models.BooleanField(blank=False, default=True, verbose_name='فعال')
    owner_created_at = models.DateTimeField(blank=False,auto_now_add=True, max_length=100,verbose_name="تاریخ ایجاد کاربر")
    owner_updated_at = models.DateTimeField(blank=False,auto_now=True, max_length=100,verbose_name="آخرین میزکار")

    def __str__(self) :
        return self.owner_name


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
    # vd_browser_port = models.CharField(blank=True, max_length=255,verbose_name=" پورت فایل منیجر")
    # vd_port = models.CharField(blank=True, max_length=25,verbose_name=" پورت میزکار")
    vd_server = models.ForeignKey('VDIServer',on_delete=models.DO_NOTHING,verbose_name="سرور")
    vd_owner = models.ForeignKey('UserProfile',on_delete=models.CASCADE,verbose_name="تحویل گیرنده")
    # vd_owner = models.CharField(blank=True, max_length=255,verbose_name="نام تحویل گیرنده")
    vd_letter_number = models.IntegerField(blank=True,default=1111,verbose_name="شماره نامه")
    vd_description = models.TextField(blank=True, verbose_name="توضیحات")
    vd_creator_ip = models.CharField(blank=True,max_length=255, verbose_name=" آیپی ایجاد کننده")
    vd_is_activate = models.BooleanField(blank=False,default=True, verbose_name="فعال")
    vd_created_by = models.CharField(blank=True, max_length=255,verbose_name="ایجاد کننده")
    vd_created_at = models.DateTimeField(blank=False,auto_now_add=True, verbose_name="تاریخ ایجاد")
    vd_revoked_at = models.DateTimeField(blank=True,default=get_expiry_time(), verbose_name="تاریخ ابطال")
    vd_expired_at = models.DateTimeField(blank=False,auto_now=True, verbose_name="تاریخ انقضا")

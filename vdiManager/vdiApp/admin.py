from django.contrib import admin

from vdiApp.models import VDIServer,VirtualDesktop


class VirtualDesktopAdmin(admin.ModelAdmin):
    date_hierarchy = 'vd_created_at'
    empty_value_display = '-empty-'
    list_display = ['vd_container_name','vd_container_cpu','vd_container_mem','vd_container_img','vd_container_id','vd_server',
                'vd_owner','vd_letter_number','vd_description','vd_creator_ip','vd_created_by','vd_is_activate','vd_created_at',
                'vd_revoked_at','vd_expired_at'
    ]
    search_fields = ['cert_owner','vd_letter_number','vd_created_by']
class VDIServerAdmin(admin.ModelAdmin):
    pass

admin.site.register(VirtualDesktop,VirtualDesktopAdmin)
admin.site.register(VDIServer,VDIServerAdmin)
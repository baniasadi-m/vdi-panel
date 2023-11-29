from django.contrib import admin

from vdiApp.models import VDIServer,VirtualDesktop,UserProfile,VDIInfo


class VirtualDesktopAdmin(admin.ModelAdmin):
    date_hierarchy = 'vd_created_at'
    empty_value_display = '-empty-'
    list_display = ['vd_container_name','vd_container_cpu','vd_container_mem','vd_container_img','vd_container_id',
                'vd_owner','vd_letter_number','vd_description','vd_creator_ip','vd_created_by','vd_is_activate','vd_created_at',
                'vd_revoked_at','vd_expired_at'
    ]
    search_fields = ['vd_owner','vd_letter_number','vd_created_by']
class VDIServerAdmin(admin.ModelAdmin):
    list_display = ['server_name','server_ip','server_port','server_hostname','is_enabled']

class UserProfileAdmin(admin.ModelAdmin):
    list_display=['owner_name','owner_user','owner_ip','owner_browser_ip','owner_vd_created_number','owner_created_at','owner_updated_at']

class VDIInfoAdmin(admin.ModelAdmin):
    list_display = ['company_short_name','company_name','limit_user','expired_at']
admin.site.register(VirtualDesktop,VirtualDesktopAdmin)
admin.site.register(VDIServer,VDIServerAdmin)
admin.site.register(UserProfile,UserProfileAdmin)
admin.site.register(VDIInfo,VDIInfoAdmin)
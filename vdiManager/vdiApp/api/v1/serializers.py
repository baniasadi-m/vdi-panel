from rest_framework import serializers
from ...models import VirtualDesktop,VDIServer,UserProfile

class VDISerializer(serializers.ModelSerializer):
    class Meta:
        model = VirtualDesktop
        fields =['id','vd_container_name','vd_container_user'
                 ,'vd_container_password','vd_browser_pass','vd_container_vncpass'
                 ,'vd_owner','vd_creator_ip'
                 ,'vd_is_activate','vd_created_by','vd_created_at','vd_revoked_at'
                 ,'vd_expired_at'
        ]

class ServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = VDIServer
        fields= ['id','server_name','server_ip','data_path','server_port','server_scheme','server_hostname','is_enabled','description']

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id','owner_name','owner_user','owner_password','owner_server','owner_ip','owner_browser_ip',
                  'owner_vd_created_number','owner_description','owner_create_by_ldap',
                  'owner_is_active','owner_created_at','owner_updated_at']


class VDIPostSerializer(serializers.ModelSerializer):
    vd_server = ServerSerializer()
    # vd_server = serializers.PrimaryKeyRelatedField(source ='server',many=True,queryset= VDIServer.objects.all(),required=False)
    
    class Meta:
        model = VirtualDesktop
        fields =['id','vd_container_name','vd_container_user','vd_container_password','vd_container_vncpass',
        'vd_port','vd_browser_port','vd_owner','vd_creator_ip','vd_container_cpu','vd_container_mem',
        'vd_container_img','vd_created_by','vd_server'
        ]
    def create(self, validated_data):
        print("validated_data",validated_data)
        return VirtualDesktop.objects.create(**validated_data)
    # def save(self, **kwargs):
    #     self.validated_data.pop("server")

    #     return super().save(**kwargs)

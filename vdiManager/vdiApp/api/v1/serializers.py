from rest_framework import serializers
from ...models import VirtualDesktop,VDIServer

class VDISerializer(serializers.ModelSerializer):
    server_ip = serializers.CharField(source='vd_server.server_ip',read_only=True)
    class Meta:
        model = VirtualDesktop
        fields =['id','vd_container_name','vd_container_user','vd_container_password','vd_container_vncpass',
        'vd_port','vd_browser_port','server_ip','vd_owner'
        ]

class ServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = VDIServer
        fields= ['id','server_name','server_ip','data_path','server_port','server_scheme']



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

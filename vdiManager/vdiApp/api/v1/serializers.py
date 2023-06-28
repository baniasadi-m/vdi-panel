from rest_framework import serializers
from ...models import VirtualDesktop

class VDISerializer(serializers.ModelSerializer):
    server_ip = serializers.CharField(source='vd_server.server_ip',read_only=True)
    class Meta:
        model = VirtualDesktop
        fields =['id','vd_container_name','vd_container_user','vd_container_password','vd_container_vncpass',
        'vd_port','vd_browser_port','server_ip','vd_owner'
        ]

class VDIPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = VirtualDesktop
        fields =['__all__']

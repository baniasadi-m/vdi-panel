from rest_framework import serializers
from ...models import VirtualDesktop
class VDISerializer(serializers.ModelSerializer):
    class Meta:
        model = VirtualDesktop
        fields =['vd_container_name','vd_container_user','vd_container_password','vd_container_vncpass',
        'vd_port','vd_server','vd_owner','vd_letter_number','vd_description'
        ]

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import VDISerializer,VDIPostSerializer
from ...models import VirtualDesktop
from ...config import Config
from ...util import get_client_ip, get_current_datetime, get_server, user_allowed, server_status

from django.shortcuts import get_object_or_404

@api_view(['GET','POST'])
def api_vdesktops(request,id=None):
    if request.method == 'GET' and id==None:
        try:
            vds = VirtualDesktop.objects.all()
            serializer = VDISerializer(vds,many=True)
            print(get_client_ip(request))
            return Response(serializer.data)
        except VirtualDesktop.DoesNotExist:
            return Response({"detaile":"Not Found"},status=status.HTTP_404_NOT_FOUND)
    
    elif request.method == 'GET' and id != None:
        vd = get_object_or_404(VirtualDesktop, pk=id)
        serializer = VDISerializer(vd)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = VDIPostSerializer(data=request.data)
        serializer.vd_container_name = request.data['vd_container_name']
        serializer.vd_container_user= request.data['vd_container_user']
        serializer.vd_container_password = request.data['vd_container_password']
        serializer.vd_container_vncpass= request.data['vd_container_vncpass']
        serializer.vd_owner = request.data['vd_owner']
        serializer.vd_created_by = request.data['vd_created_by']
        serializer.vd_creator_ip = get_client_ip(request)
        serializer.vd_container_cpu = '2'
        serializer.vd_container_mem = '2g'
        serializer.vd_container_img = Config.DOCKER_DESKTOP_IMAGE
        serializer.vd_server = get_server()

        url = f"{temp_form.vd_server.server_scheme}://{temp_form.vd_server.server_ip}:{temp_form.vd_server.server_port}/api/v1/containers"
        headers={'Content-Type': 'application/json'}
        data = {
                'image': f"{serializer.vd_container_img}",
                'name' : f"{serializer.vd_container_name}",
                'cpu' : f"{serializer.vd_container_cpu}",
                'mem' : f"{serializer.vd_container_mem}",
                'volumes' : {f"{temp_form.vd_server.data_path}/{serializer.vd_container_name}/Downloads": {'bind': f"/home/{temp_form.vd_container_user}/Downloads", 'mode': 'rw'}},
                'env' : {"USER":f"{serializer.vd_container_user}","PASSWORD":f"{temp_form.vd_container_password}","VNC_PASSWORD":f"{temp_form.vd_container_vncpass}"},
                'ports' : ['80'],
                # 'ports' : {'80/tcp':int(f"{temp_form.vd_port}")},
                }
        print(data)
        import requests, json
        try:
            r = requests.post(url=url,data=json.dumps(data),headers=headers,verify=False).json()
            print(type(r),r)
            response_ports = json.loads(r['container_spec']['host_ports'])
            if len(response_ports) > 1:
                for i in response_ports:
                    temp_form.vd_port += f",{str(i)}"
            else:
                temp_form.vd_port = response_ports[0]
        except Exception as e:
            print(e)


        if serializer.is_valid(raise_exception=True):
            
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

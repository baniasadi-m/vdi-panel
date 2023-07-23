from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import VDISerializer,VDIPostSerializer
from ...models import VirtualDesktop,VDIServer
from vdiManager.settings import Config
from ...util import get_client_ip, get_server, jwt_gen_token

from django.shortcuts import get_object_or_404

@api_view(['GET','POST'])
def api_vdesktops(request,id=None):
    if request.method == 'GET' and id==None:
        try:
            vds = VirtualDesktop.objects.all()
            serializer = VDISerializer(vds,many=True)
            # print(get_client_ip(request))
            return Response(serializer.data)
        except VirtualDesktop.DoesNotExist:
            return Response({"detaile":"Not Found"},status=status.HTTP_404_NOT_FOUND)
    
    elif request.method == 'GET' and id != None:
        vd = get_object_or_404(VirtualDesktop, pk=id)
        serializer = VDISerializer(vd)
        return Response(serializer.data)
    elif request.method == 'POST':
        mydata = request.data
        elect_server = get_server()
        print(type(elect_server))
        other_data = {
            "vd_container_cpu" : '2',
            "vd_container_mem" : '2g',
            "vd_container_img" : f"{Config.DOCKER_DESKTOP_IMAGE}",
            "vd_creator_ip" : f"{get_client_ip(request)}",
            "vd_server" : elect_server
 
                # {
                #     "id": f"{elect_server.id}",
                #     "server_name": f"{elect_server.server_name}",
                #     "server_ip": f"{elect_server.server_ip}",
                #     "data_path": f"{elect_server.data_path}",
                #     "server_port": f"{elect_server.server_port}",
                #     "server_scheme": f"{elect_server.server_scheme}",
                #     "description": f"{elect_server.description}",

                # }
            
        }

        mydata.update(other_data)
        serializer = VDIPostSerializer(data=mydata)
        print(serializer)


        # serializer.vd_container_name = request.data['vd_container_name']
        # serializer.vd_container_user= request.data['vd_container_user']
        # serializer.vd_container_password = request.data['vd_container_password']
        # serializer.vd_container_vncpass= request.data['vd_container_vncpass']
        # serializer.vd_owner = request.data['vd_owner']
        # serializer.vd_created_by = request.data['vd_created_by']
        # serializer.vd_creator_ip = get_client_ip(request)
        # serializer.vd_container_cpu = '2'
        # serializer.vd_container_mem = '2g'
        # serializer.vd_container_img = Config.DOCKER_DESKTOP_IMAGE

        # print(type(elect_server),elect_server)

        url = f"{elect_server.server_scheme}://{elect_server.server_ip}:{elect_server.server_port}/api/v1/containers"
        # url = f"{serializer.server.server_scheme}://{serializer.server.server_ip}:{serializer.server.server_port}/api/v1/containers"
        headers={'Content-Type': 'application/json'}
        jwt_token = jwt_gen_token()
        headers.update(
            {
                'jwt': f"{jwt_token}"
            }
        )
        data = {
                'image': f"{mydata['vd_container_img']}",
                'name' : f"{mydata['vd_container_name']}",
                'cpu' : f"{mydata['vd_container_cpu']}",
                'mem' : f"{mydata['vd_container_mem']}",
                'volumes' : {f"{elect_server.data_path}/{mydata['vd_container_name']}/Downloads": {'bind': f"/home/{mydata['vd_container_user']}/Downloads", 'mode': 'rw'}},
                'env' : {"USER":f"{mydata['vd_container_user']}","PASSWORD":f"{mydata['vd_container_password']}","VNC_PASSWORD":f"{mydata['vd_container_vncpass']}"},
                'ports' : ['80'],
                # 'ports' : {'80/tcp':int(f"{temp_form.vd_port}")},
                }
        # print(data)
        import requests, json
        # try:
            # r = requests.post(url=url,data=json.dumps(data),headers=headers,verify=False).json()
            # print(type(r),r)
        #     response_ports = json.loads(r['container_spec']['host_ports'])
        #     if len(response_ports) > 1:
        #         for i in response_ports:
        #             serializer.vd_port += f",{str(i)}"
        #     else:
        #         serializer.vd_port = response_ports[0]
        # except Exception as e:
        #     print(e)

        # print("init data:",serializer.initial_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


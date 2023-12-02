from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import VDISerializer,VDIPostSerializer,ServerSerializer,ProfileSerializer
from ...models import VirtualDesktop,VDIServer,UserProfile
from vdiManager.settings import Config
from django.forms.models import model_to_dict
from ...util import get_client_ip, get_server, jwt_gen_token, server_status,create_container, gen_password, get_free_ip

from django.shortcuts import get_object_or_404

@api_view(['GET','POST','DELETE'])
def api_vdesktops(request,id=None):
    if request.method == 'GET' and id==None:
        try:
            vds = VirtualDesktop.objects.all()
            print(vds)
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
        server = get_server()
        vdi_name = f"{mydata['vd_container_user']}-vdi"
        browser_name = f"{mydata['vd_container_user']}-filebrowser"
        vnc_pass = gen_password()
        password = request.data['vd_container_password']
        creator_ip = get_client_ip(request)
        container_ip = get_free_ip(server=server)
        container = create_container(server,image=f"{Config.DOCKER_DESKTOP_IMAGE}"
                                    ,name=f"{vdi_name}"
                                    ,cpu='2'
                                    ,mem='2g'
                                    ,volumes={f"{server.data_path}/{vdi_name}/Downloads": {'bind': f"/home/{mydata['vd_container_user']}/Downloads", 'mode': 'rw'}}
                                    ,env={"USER":f"{mydata['vd_container_user']}","PASSWORD":f"{password}aqr","VNC_PASSWORD":f"{vnc_pass}","RELATIVE_URL_ROOT":f"{mydata['vd_container_user']}","HTTP_PROXY":f"{mydata['vd_container_user']}:{password}@172.20.0.2:3128","HTTPS_PROXY":f"{mydata['vd_container_user']}:{password}@172.20.0.2:3128"}
                                    ,network='no-internet'
                                    ,ip=container_ip
                                    )
        if int(container['result']) == 1:
            vdi_id = container['container_spec']['id']
            vdi_shortid = container['container_spec']['shortid']
            fb_password = gen_password()
            fb_container = create_container(server,image=f"{Config.DOCKER_BROWSER_IMAGE}"
                                    ,name=f"{browser_name}"
                                    ,cpu='1'
                                    ,mem='1g'
                                    ,volumes={f"{server.data_path}/{vdi_name}/Downloads": {'bind': f"/srv", 'mode': 'ro'}}
                                    ,env={"FBUSER":f"{mydata['vd_container_user']}","FBPASSWORD":f"{fb_password}","BASEURL":f"/{mydata['vd_container_user']}/fbrowser"}
                                    ,network='no-internet'
                                    ,ip=f"{owner.owner_browser_ip}"
                                    )
        # print(type(elect_server))
        # other_data = {
        #     "vd_container_cpu" : '2',
        #     "vd_container_mem" : '2g',
        #     "vd_container_img" : f"{Config.DOCKER_DESKTOP_IMAGE}",
        #     "vd_creator_ip" : f"{get_client_ip(request)}",
        #     "vd_server" : elect_server
 
                # {
                #     "id": f"{elect_server.id}",
                #     "server_name": f"{elect_server.server_name}",
                #     "server_ip": f"{elect_server.server_ip}",
                #     "data_path": f"{elect_server.data_path}",
                #     "server_port": f"{elect_server.server_port}",
                #     "server_scheme": f"{elect_server.server_scheme}",
                #     "description": f"{elect_server.description}",

                # }
            
        # }

        # mydata.update(other_data)
        # serializer = VDIPostSerializer(data=mydata)
        # print(serializer)


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

        # url = f"{elect_server.server_scheme}://{elect_server.server_ip}:{elect_server.server_port}/api/v1/containers"
        # # url = f"{serializer.server.server_scheme}://{serializer.server.server_ip}:{serializer.server.server_port}/api/v1/containers"
        # headers={'Content-Type': 'application/json'}
        # jwt_token = jwt_gen_token()
        # headers.update(
        #     {
        #         'jwt': f"{jwt_token}"
        #     }
        # )
        # data = {
        #         'image': f"{mydata['vd_container_img']}",
        #         'name' : f"{mydata['vd_container_name']}",
        #         'cpu' : f"{mydata['vd_container_cpu']}",
        #         'mem' : f"{mydata['vd_container_mem']}",
        #         'volumes' : {f"{elect_server.data_path}/{mydata['vd_container_name']}/Downloads": {'bind': f"/home/{mydata['vd_container_user']}/Downloads", 'mode': 'rw'}},
        #         'env' : {"USER":f"{mydata['vd_container_user']}","PASSWORD":f"{mydata['vd_container_password']}","VNC_PASSWORD":f"{mydata['vd_container_vncpass']}"},
        #         'ports' : ['80'],
                # 'ports' : {'80/tcp':int(f"{temp_form.vd_port}")},
                # }
        # print(data)
        # import requests, json
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
        # serializer.is_valid(raise_exception=True)
        # serializer.save()
        # return Response(serializer.data)
    elif request.method == 'DELETE':
        if id == None:
            return Response({"detaile":"Not Found"},status=status.HTTP_501_NOT_IMPLEMENTED)
        vd = get_object_or_404(VirtualDesktop, pk=id)
        serializer = ServerSerializer(vd)
        vd.delete()
        return Response(serializer.data)


@api_view(['GET','POST','DELETE','PUT'])
def api_servers(request,id=None):
    if request.method == 'GET' and id == None:
        try:
            vds = VDIServer.objects.all()
            serializer = ServerSerializer(vds,many=True)
            # print(get_client_ip(request))
            return Response(serializer.data)
        except VirtualDesktop.DoesNotExist:
            return Response({"detaile":"Not Found"},status=status.HTTP_404_NOT_FOUND)
    elif request.method == 'GET' and id != None:
        vd = get_object_or_404(VDIServer, pk=id)
        serializer = ServerSerializer(vd)
        return Response(serializer.data)
    elif request.method == 'POST':
        if id != None:
            return Response({"detaile":"Not Found"},status=status.HTTP_501_NOT_IMPLEMENTED)
        mydata = request.data
        print(mydata)
        serializer = ServerSerializer(data=mydata)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
       
    elif request.method == 'PUT':
        if id == None:
            return Response({"detaile":"Not Found"},status=status.HTTP_501_NOT_IMPLEMENTED)
        mydata = request.data
        server = get_object_or_404(VDIServer, pk=id)

        serializer = ServerSerializer(instance=server,data=mydata, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    elif request.method == 'DELETE':
        if id == None:
            return Response({"detaile":"Not Found"},status=status.HTTP_501_NOT_IMPLEMENTED)
        vd = get_object_or_404(VDIServer, pk=id)
        serializer = ServerSerializer(vd)
        vd.delete()
        return Response(serializer.data)

@api_view(['GET','POST','DELETE','PUT'])
def server_check(request,id=None):
    if request.method == 'GET' and id == None:
        try:
            server = get_object_or_404(VDIServer, pk=id)
            url = f"{server.server_scheme}://{server.server_ip}:{server.server_port}/api/v1/load"
            output = {}
            if server_status(server_url=url) == True:
                output.update({
                    'server' : server.server_name,
                    'status' : 'Running'

                })
            else:
                output.update({
                    'server' : server.server_name,
                    'status' : 'Failed'

                })           
                # serializer = ServerSerializer(server,many=True)
                # print(get_client_ip(request))
            return Response(output)
        except VirtualDesktop.DoesNotExist:
            return Response({"detaile":"Not Found"},status=status.HTTP_404_NOT_FOUND)
 

@api_view(['GET','POST','DELETE','PUT'])
def api_profiles(request,id=None):
    if request.method == 'GET' and id==None:
        try:
            vds = UserProfile.objects.all()
            serializer = ProfileSerializer(vds,many=True)
            return Response(serializer.data)
        except VirtualDesktop.DoesNotExist:
            return Response({"detaile":"Not Found"},status=status.HTTP_404_NOT_FOUND)
    elif request.method == 'GET' and id != None:
        vd = get_object_or_404(UserProfile, pk=id)
        serializer = ProfileSerializer(vd)
        return Response(serializer.data)
    elif request.method == 'POST':
        if id != None:
            return Response({"detaile":"Not Found"},status=status.HTTP_501_NOT_IMPLEMENTED)       
        mydata = request.data
        print(mydata)
        serializer = ProfileSerializer(data=mydata)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
       
    elif request.method == 'PUT':
        if id == None:
            return Response({"detaile":"Not Found"},status=status.HTTP_501_NOT_IMPLEMENTED)
        mydata = request.data
        profile = get_object_or_404(UserProfile, pk=id)
        serializer = ProfileSerializer(instance=profile,data=mydata, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    elif request.method == 'DELETE':
        if id == None:
            return Response({"detaile":"Not Found"},status=status.HTTP_501_NOT_IMPLEMENTED)
        vd = get_object_or_404(UserProfile, pk=id)
        serializer = ProfileSerializer(vd)
        vd.delete()
        return Response(serializer.data)

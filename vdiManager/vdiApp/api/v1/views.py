from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from .serializers import VDISerializer,VDIPostSerializer,ServerSerializer,ProfileSerializer
from ...models import VirtualDesktop,VDIServer,UserProfile
from vdiManager.settings import Config
from django.forms.models import model_to_dict
from ...util import api_check,get_client_ip, update_nginx, get_server, jwt_gen_token, server_status,create_container,gen_password, get_free_ip,get_profile_or_None,get_vd_or_None,get_expiry_time,profile_update_password,getUsersInGroup

from django.shortcuts import get_object_or_404

@api_view(['GET','POST','DELETE'])
def api_vdesktops(request,id=None):
    if api_check() == False:
        return Response({"error":"Your License is Not Valid"},status=status.HTTP_401_UNAUTHORIZED)
    paginator = PageNumberPagination()
    paginator.page_size = 10
    if request.method == 'GET' and id==None:
        try:
            vds = VirtualDesktop.objects.all()
            print(vds)
            result_page = paginator.paginate_queryset(vds, request)
            serializer = VDISerializer(result_page,many=True)
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
        password = request.data['vd_container_password']
        username = request.data['vd_container_user']
        is_ldap = request.data['is_ldap']
        profile  = get_profile_or_None(user=username,password=password)
        server = get_server()
        vdi_name = f"{username}-vdi"
        browser_name = f"{username}-filebrowser"
        vnc_pass = gen_password()
        creator_ip = get_client_ip(request)
        container_ip = get_free_ip(server=server)
        if is_ldap == False:
            if profile == None:
                return Response({"detaile":"Not Found"},status=status.HTTP_404_NOT_FOUND)
            elif profile != None and profile.owner_is_active and profile.owner_create_by_ldap == False:
                vd = get_vd_or_None(container_user=username,is_activate=True)
                if vd != None :
                    serializer = VDIPostSerializer(data=vd)
                    return Response(serializer.data)
                else:
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
                                                ,ip=f"{profile.owner_browser_ip}"
                                                )
                        if int(fb_container['result']) == 1:
                            try:
                                vd_data = {
                                    'vd_container_name' :f"{vdi_name}",
                                    'vd_container_cpu' :'2',
                                    'vd_container_mem':'2g',
                                    'vd_container_img': f"{Config.DOCKER_DESKTOP_IMAGE}",
                                    'vd_container_id' :f"{vdi_id}",
                                    'vd_container_shortid' :f"{vdi_shortid}",
                                    'vd_container_user' :f"{username}",
                                    'vd_container_password' : f"{password}",
                                    'vd_container_vncpass' : f"{vnc_pass}",
                                    'vd_browser_pass' : f"{fb_password}",
                                    'vd_owner' : f"{profile.pk}",
                                    'vd_description' : f"created vdi by local users",
                                    'vd_browser_id' : f"{fb_container['container_spec']['id']}",
                                    'vd_browser_img' : f"{Config.DOCKER_BROWSER_IMAGE}",
                                    'vd_browser_name' :f"{browser_name}",
                                    'vd_is_activate' : True,
                                    'vd_created_by' : f"LOCAL-{username}",
                                    'vd_creator_ip' : f"{creator_ip}",
                                    'vd_expired_at' : f"{get_expiry_time()}"
                                }
                                nginx_result = update_nginx(server=server,user=f"{username}",vd_container=f"{vdi_name}",fb_container=f"{browser_name}")
                                if int(nginx_result['result']) == 1:
                                    serializer = VDIPostSerializer(data=vd_data)
                                    serializer.is_valid(raise_exception=True)
                                    serializer.save()
                                    return Response(serializer.data)
                            except Exception as e:
                                return Response({"detaile":f"{e}"},status=status.HTTP_404_NOT_FOUND)
        else:
            ldap_user = getUsersInGroup(server_ip=f"{Config.Active_Directory_ServerIP}",username= username, password= password,domain=Config.Active_Directory_DomainName,group=Config.Active_Directory_GroupName)

            if ldap_user[0] == False:
                return Response({"detaile":"Not Found"},status=status.HTTP_401_UNAUTHORIZED)
            else:
                profile = get_object_or_404(UserProfile, owner_user=username)
                profile_update_password(username=username,password=password)
                profile = get_profile_or_None(user=username,password=password)
                if profile != None and profile.owner_is_active and profile.owner_create_by_ldap == True:
                    vd = get_vd_or_None(container_user=username,is_activate=True)
                    if vd != None :
                        serializer = VDIPostSerializer(data=vd)
                        return Response(serializer.data)
                    else:
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
                                                    ,ip=f"{profile.owner_browser_ip}"
                                                    )
                            if int(fb_container['result']) == 1:
                                try:
                                    vd_data = {
                                        'vd_container_name' :f"{vdi_name}",
                                        'vd_container_cpu' :'2',
                                        'vd_container_mem':'2g',
                                        'vd_container_img': f"{Config.DOCKER_DESKTOP_IMAGE}",
                                        'vd_container_id' :f"{vdi_id}",
                                        'vd_container_shortid' :f"{vdi_shortid}",
                                        'vd_container_user' :f"{username}",
                                        'vd_container_password' : f"{password}",
                                        'vd_container_vncpass' : f"{vnc_pass}",
                                        'vd_browser_pass' : f"{fb_password}",
                                        'vd_owner' : f"{profile.pk}",
                                        'vd_description' : f"created vdi by local users",
                                        'vd_browser_id' : f"{fb_container['container_spec']['id']}",
                                        'vd_browser_img' : f"{Config.DOCKER_BROWSER_IMAGE}",
                                        'vd_browser_name' :f"{browser_name}",
                                        'vd_is_activate' : True,
                                        'vd_created_by' : f"LOCAL-{username}",
                                        'vd_creator_ip' : f"{creator_ip}",
                                        'vd_expired_at' : f"{get_expiry_time()}"
                                    }
                                    serializer = VDIPostSerializer(data=vd_data)
                                    serializer.is_valid(raise_exception=True)
                                    serializer.save()
                                    return Response(serializer.data)
                                except Exception as e:
                                    return Response({"detaile":f"{e}"},status=status.HTTP_404_NOT_FOUND)
 
    elif request.method == 'DELETE':
        if id == None:
            return Response({"detaile":"Not Found"},status=status.HTTP_501_NOT_IMPLEMENTED)
        vd = get_object_or_404(VirtualDesktop, pk=id)
        container_ids = []
        data_paths = []
        container_ids.append(vd.vd_container_id)
        container_ids.append(vd.vd_browser_id)
        data_paths.append(f"{vd.vd_owner.owner_server.data_path}/{vd.vd_container_name}")
        users=[]
        users.append(vd.vd_owner.owner_user)
        print(users)
        import requests,json
        url = f"{vd.vd_owner.owner_server.server_scheme}://{vd.vd_owner.owner_server.server_ip}:{vd.vd_owner.owner_server.server_port}/api/v1/containers"
        try:
            data = {'path':list(data_paths),'ids': list(container_ids),'user':users}
            headers={'Content-Type': 'application/json'}
            jwt_token = jwt_gen_token()
            headers.update(
                {
                    'jwt': f"{jwt_token}"
                }
            )
            r = requests.delete(url=url,headers=headers,data=json.dumps(data),verify=False).json()
            if int(r['status']) == 1:
                serializer = ServerSerializer(vd)
                vd.delete()
                return Response(serializer.data)
        except VirtualDesktop.DoesNotExist:
            return Response({"detaile":"Not Found"},status=status.HTTP_504_GATEWAY_TIMEOUT)  

@api_view(['GET','POST','DELETE','PUT'])
def api_servers(request,id=None):
    if api_check() == False:
        return Response({"error":"Your License is Not Valid"},status=status.HTTP_401_UNAUTHORIZED)
    if request.method == 'GET' and id == None:
        try:
            vds = VDIServer.objects.all()
            paginator = PageNumberPagination()
            paginator.page_size = 10
            result_page = paginator.paginate_queryset(vds, request)
            serializer = ServerSerializer(result_page,many=True)
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
    if api_check() == False:
        return Response({"error":"Your License is Not Valid"},status=status.HTTP_401_UNAUTHORIZED)
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
    if api_check() == False:
        return Response({"error":"Your License is Not Valid"},status=status.HTTP_401_UNAUTHORIZED)
    if request.method == 'GET' and id==None:
        try:
            vds = UserProfile.objects.all()
            paginator = PageNumberPagination()
            paginator.page_size = 10
            result_page = paginator.paginate_queryset(vds, request)
            serializer = ProfileSerializer(result_page,many=True)
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

@api_view(['GET'])
def search(request,q):
    if api_check() == False:
        return Response({"error":"Your License is Not Valid"},status=status.HTTP_401_UNAUTHORIZED)
    if q:
        vd = VirtualDesktop.objects.filter(Q(vd_owner__owner_ip=q) |Q(vd_owner__owner_name=q) |Q(vd_created_by__icontains=q) |Q(vd_letter_number__icontains=q) |Q(vd_container_name__icontains=q))
        # vd = get_object_or_404(UserProfile, pk=id)
        paginator = PageNumberPagination()
        paginator.page_size = 2
        result_page = paginator.paginate_queryset(vd, request)
        serializer = VDISerializer(result_page,many=True)
        return Response(serializer.data)
    else:
        return Response({"detaile":"Not Found"},status=status.HTTP_501_NOT_IMPLEMENTED)
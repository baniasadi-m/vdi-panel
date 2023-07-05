from django.shortcuts import render,HttpResponse,redirect
from vdiApp.models import VirtualDesktop
from django.contrib import messages
from vdiApp.util import ad_auth_user, get_server, gen_password, get_client_ip
from vdiApp.config import Config
# Create your views here.
def adauth_get_info(request):
    context ={}
    return render(request, 'adAuth/auth.html',context=context)
    
def adauth_list_info(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        myvdi = ad_auth_user(server_ip=f"{Config.Active_Directory_ServerIP}",username= username, password= password,domain=Config.Active_Directory_DomainName)

        if myvdi != None and myvdi[0] == True :
            vdi_name = f"{username}-vdi"
            browser_name = f"{username}-filebrowser"
            vnc_pass = gen_password()
            container_ports=""
            browser_port=""
            creator_ip = get_client_ip(request)

            server = get_server()
            import requests, json

            url = f"{server.server_scheme}://{server.server_ip}:{server.server_port}/api/v1/containers"
            headers={'Content-Type': 'application/json'}
            data = {
                    'image': f"{Config.DOCKER_DESKTOP_IMAGE}",
                    'name' : f"{vdi_name}",
                    'cpu' : f"2",
                    'mem' : f"2g",
                    'volumes' : {f"{server.data_path}/{vdi_name}/Downloads": {'bind': f"/home/{username}/Downloads", 'mode': 'rw'}},
                    'env' : {"USER":f"{username}","PASSWORD":f"{password}aqr","VNC_PASSWORD":f"{vnc_pass}"},
                    'ports' : ['80'],
                    }
            try:
                r = requests.post(url=url,data=json.dumps(data),headers=headers,verify=False).json()

                vdi_id = r['container_spec']['id']
                vdi_shortid = r['container_spec']['short_id']

                response_ports = json.loads(r['container_spec']['host_ports'])
                if len(response_ports) > 1:
                    for i in response_ports:
                        container_ports += f",{str(i)}"
                else:
                    container_ports = response_ports[0]
            except Exception as e:
                print(e)
                messages.add_message(request,messages.ERROR,'API error')
                return redirect('/')
            
            try:

                data = {
                        'image': f"{Config.DOCKER_BROWSER_IMAGE}",
                        'name' : f"{browser_name}",
                        'cpu' : "2",
                        'mem' : "1g",
                        'volumes' : {f"{server.data_path}/{vdi_name}/Downloads": {'bind': f"/srv", 'mode': 'ro'}},
                        'env' : {"USER":"vdi"},
                        'ports' : ['80'],
                        }
                r = requests.post(url=url,data=json.dumps(data),headers=headers,verify=False).json()

                if int(r['status']) == 1:
                    
                    browser_id = r['container_spec']['id']
                    browser_ports = json.loads(r['container_spec']['host_ports'])
                    if len(response_ports) > 1:
                        for i in browser_ports:
                            browser_port += f",{str(i)}"
                    else:
                        browser_port = browser_ports[0]
            except Exception as e:
                print(e)
                messages.add_message(request,messages.ERROR,'API error')
                return redirect('/')
            try:
                vdi_model = VirtualDesktop.objects.create(vd_container_name=f"{vdi_name}",
                                                        vd_server=server,
                                                        vd_container_cpu='2',
                                                        vd_container_mem='2g',
                                                        vd_container_img=Config.DOCKER_DESKTOP_IMAGE,
                                                        vd_container_id=f"{vdi_id}",
                                                        vd_container_shortid=f"{vdi_shortid}",
                                                        vd_container_user=f"{username}",
                                                        vd_container_password=f"{password}",
                                                        vd_container_vncpass=f"{vnc_pass}",
                                                        vd_port=f"{container_ports}",
                                                        vd_owner=f"{username}",
                                                        vd_description=f"created vdi by active directory users",
                                                        vd_browser_id=f"{browser_id}",
                                                        vd_browser_port=f"{browser_port}",
                                                        vd_browser_img=f"{Config.DOCKER_BROWSER_IMAGE}",
                                                        vd_browser_name=f"{browser_name}",
                                                        vd_is_activate = True,
                                                        vd_created_by =f"ad-{username}",
                                                        vd_creator_ip=f"{creator_ip}"
                                                        )
                vdi_name=f"{vdi_name}"
                vdi_url=f"{server.server_scheme}://{server.server_ip}:{container_ports}"
                vdi_vncpass=f"{vnc_pass}"
                vdi_browser_url=f"{server.server_scheme}://{server.server_ip}:{browser_port}"
                vdi_browser_user='admin'
                vdi_browser_pass='admin'
                vdi_created_at= vdi_model.vd_created_at
                vdi_expired_at= vdi_model.vd_expired_at

                context ={
                    'vdi_name':f"{vdi_name}",
                    'vdi_url': f"{vdi_url}",
                    'vdi_vncpass':f"{vdi_vncpass}",
                    'vdi_browser_url':f"{vdi_browser_url}",
                    'vdi_browser_user':f"{vdi_browser_user}",
                    'vdi_browser_pass':f"{vdi_browser_pass}",
                    'vdi_created_at':f"{vdi_created_at}",
                    'vdi_expired_at':f"{vdi_expired_at}",
                }
                return render(request, 'adAuth/info.html',context=context)
                

            except Exception as e:
                print(e)
                messages.add_message(request,messages.ERROR,e)
                return redirect('/')

        elif myvdi[0] == False:
            messages.add_message(request,messages.WARNING,myvdi[1])
            return redirect('/')

    return redirect('/')


  
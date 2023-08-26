from django.shortcuts import render,HttpResponse,redirect
from vdiApp.models import VirtualDesktop, UserProfile
from django.db.models import Q
from django.contrib import messages
from vdiApp.util import *
from vdiManager.settings import Config
from .forms import CaptchaLoginForm
from datetime import datetime
import re
# Create your views here.
def adauth_get_info(request):
    form = CaptchaLoginForm()
    context ={'captcha_form': form}
    return render(request, 'adAuth/login.html',context=context)

def create_vdi():
    pass



    

def adauth_list_info(request):
    if request.method == 'POST':
        form = CaptchaLoginForm(request.POST)
        if form.is_valid():      
            ip_pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')      
            username = request.POST['username']
            password = request.POST['password']
            if 'ad_auth' in request.POST:
                Active_Directory_Enabled = True
            else:
                request.POST.get('ad_auth',False)

                Active_Directory_Enabled = False

            
            
            try:
                ##### Local Authentication#################
                if Active_Directory_Enabled == False:
                    owner = get_profile_or_None(user=username,password=password)
                    print("DEBUG",owner)
                    if owner == None:
                        print("Owner not found")
                        messages.add_message(request,messages.ERROR,'username or password is incorrect')
                        return redirect('/')
                    #### Profile is active
                    elif owner != None and owner.owner_is_active and owner.owner_create_by_ldap == False:
                        owner_vd = get_vd_or_None(container_user=username,is_activate=True)
                        print(owner_vd)
                        
                        #### VDI is active
                        if owner_vd != None:
                            if owner_vd.vd_is_activate == True:

                                print("active VD",owner_vd.vd_server)

                                vdi_name=f"{owner_vd.vd_container_name}"
                                vdi_url=f"{owner_vd.vd_server.server_scheme}://{owner_vd.vd_server.server_hostname}/{username}/"
                                vdi_vncpass=f"{owner_vd.vd_container_vncpass}"
                                vdi_browser_url=f"{owner_vd.vd_server.server_scheme}://{owner_vd.vd_server.server_hostname}/{username}/browser"
                                vdi_browser_user=f"{username}"
                                vdi_browser_pass=f"{owner_vd.vd_browser_pass}"
                                vdi_created_at= owner_vd.vd_created_at
                                vdi_expired_at= owner_vd.vd_expired_at

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
                 
                        #### create VDI
                        else:
                            
                            vdi_name = f"{username}-vdi"
                            browser_name = f"{username}-filebrowser"
                            vnc_pass = gen_password()
                            
                            creator_ip = get_client_ip(request)
                            print("DEBUG THIS:",vdi_name,browser_name,vnc_pass,creator_ip)
                            server = get_server()
                            print("VDI")
                            
                            container = create_container(server,image=f"{Config.DOCKER_DESKTOP_IMAGE}"
                                                        ,name=f"{vdi_name}"
                                                        ,cpu='2'
                                                        ,mem='2g'
                                                        ,volumes={f"{server.data_path}/{vdi_name}/Downloads": {'bind': f"/home/{username}/Downloads", 'mode': 'rw'}}
                                                        ,env={"USER":f"{username}","PASSWORD":f"{password}aqr","VNC_PASSWORD":f"{vnc_pass}","RELATIVE_URL_ROOT":f"{username}","HTTP_PROXY":f"{username}:{password}@172.20.0.2:3128","HTTPS_PROXY":f"{username}:{password}@172.20.0.2:3128"}
                                                        ,network='no-internet'
                                                        ,ip=f"{owner.owner_ip}"
                                                        )
                            print(container['result'])
                            if int(container['result']) == 1:
                                vdi_id = container['container_spec']['id']
                                vdi_shortid = container['container_spec']['shortid']
                                fb_password = gen_password()
                                fb_container = create_container(server,image=f"{Config.DOCKER_BROWSER_IMAGE}"
                                                        ,name=f"{browser_name}"
                                                        ,cpu='1'
                                                        ,mem='1g'
                                                        ,volumes={f"{server.data_path}/{vdi_name}/Downloads": {'bind': f"/srv", 'mode': 'ro'}}
                                                        ,env={"FBUSER":f"{username}","FBPASSWORD":f"{fb_password}","BASEURL":f"/{username}/fbrowser"}
                                                        ,network='no-internet'
                                                        ,ip=f"{owner.owner_browser_ip}"
                                                        )
                                print(fb_container)
                                if int(fb_container['result']) == 1:
                                    try:
                                        owner.owner_vd_created_number += 1
                                        owner.save() 
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
                                                                                vd_browser_pass = f"{fb_password}",
                                                                                vd_owner=owner,
                                                                                vd_description=f"created vdi by local users",
                                                                                vd_browser_id=f"{fb_container['container_spec']['id']}",
                                                                                vd_browser_img=f"{Config.DOCKER_BROWSER_IMAGE}",
                                                                                vd_browser_name=f"{browser_name}",
                                                                                vd_is_activate = True,
                                                                                vd_created_by =f"LDAP-{username}",
                                                                                vd_creator_ip=f"{creator_ip}"
                                                                                )
                                        vdi_name=f"{vdi_name}"
                                        vdi_url=f"{server.server_scheme}://{server.server_hostname}/{username}/"
                                        vdi_vncpass=f"{vnc_pass}"
                                        vdi_browser_url=f"{server.server_scheme}://{server.server_hostname}/{username}/fbrowser"
                                        vdi_browser_user=f"{owner.owner_user}"
                                        vdi_browser_pass=f"{vdi_model.vd_browser_pass}"
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
                                        result = update_nginx(server=server,user=f"{username}",vd_container=f"{vdi_name}",fb_container=f"{browser_name}")
                                        print(f"result2: {result}")
                                        if int(result['result']) == 1:
                                            return render(request, 'adAuth/info.html',context=context)                        
                                        return render(request, 'adAuth/info.html',context=context)
                                    except Exception as e:
                                        print(e)
                                        remove_vdi(server,user=[f"{username}"],containers=[container['container_spec']['id'],fb_container['container_spec']['id']],paths=[f"{server.data_path}/{username}-vdi"])
                                        messages.add_message(request,messages.ERROR,e)
                                        return redirect('/')
                                else:
                                    messages.add_message(request,messages.ERROR,f'API error')
                                    return redirect('/')
                            else:
                                messages.add_message(request,messages.ERROR,'API Error')
                                return redirect('/')
                    else:
                        messages.add_message(request,messages.ERROR,'Your Account not Activate localy')
                        return redirect('/')
                ###########################################
                ##### LDAP Authentication #################
                ###########################################
                else:
                    
                    ldap_user = getUsersInGroup(server_ip=f"{Config.Active_Directory_ServerIP}",username= username, password= password,domain=Config.Active_Directory_DomainName,group=Config.Active_Directory_GroupName)
                    ### ldap Auth Failure
                    print("LDAP:",ldap_user)
                    if ldap_user[0] == False:
                        print(ldap_user[1])
                        messages.add_message(request,messages.ERROR,'Authentication Failed')
                        return redirect('/')
                    elif ldap_user[0] == True:
                        profile_update_password(username=username,password=password)
                        owner = get_profile_or_None(user=username,password=password)
                        print("owner",owner)
                        if owner != None:  
                            if owner.owner_is_active == True and owner.owner_create_by_ldap == True:  
                                owner_vd = get_vd_or_None(container_user=username,is_activate=True)
                               
                                #### VDI is active  profile = 1  - vdi = 1
                                if owner_vd != None and owner_vd.vd_is_activate ==True:
                                    vdi_name=f"{owner_vd.vd_container_name}"
                                    vdi_url=f"{owner_vd.vd_server.server_scheme}://{owner_vd.vd_server.server_hostname}/{username}/"
                                    vdi_vncpass=f"{owner_vd.vd_container_vncpass}"
                                    vdi_browser_url=f"{owner_vd.vd_server.server_scheme}://{owner_vd.vd_server.server_hostname}/{username}/fbrowser"
                                    vdi_browser_user=f"{owner.owner_user}"
                                    vdi_browser_pass=f"{owner_vd.vd_browser_pass}"
                                    vdi_created_at= owner_vd.vd_created_at
                                    vdi_expired_at= owner_vd.vd_expired_at

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

                                else:
                                    ##### profile = 1  - vdi = 0                      
                                    vdi_name = f"{username}-vdi"
                                    browser_name = f"{username}-filebrowser"
                                    vnc_pass = gen_password()
                                    creator_ip = get_client_ip(request)
                                    server = get_server()
                                    container = create_container(server,image=f"{Config.DOCKER_DESKTOP_IMAGE}"
                                                                ,name=f"{vdi_name}"
                                                                ,cpu='2'
                                                                ,mem='2g'
                                                                ,volumes={f"{server.data_path}/{vdi_name}/Downloads": {'bind': f"/home/{username}/Downloads", 'mode': 'rw'}}
                                                                ,env={"USER":f"{username}","PASSWORD":f"{password}aqr","VNC_PASSWORD":f"{vnc_pass}","RELATIVE_URL_ROOT":f"{username}","HTTP_PROXY":f"{username}:{password}@172.20.0.2:3128","HTTPS_PROXY":f"{username}:{password}@172.20.0.2:3128"}
                                                                ,network='no-internet'
                                                                ,ip=f"{owner.owner_ip}"
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
                                                                ,env={"FBUSER":f"{username}","FBPASSWORD":f"{fb_password}","BASEURL":f"/{username}/fbrowser"}
                                                                ,network='no-internet'
                                                                ,ip=f"{owner.owner_browser_ip}"
                                                                )
                                        if int(fb_container['result']) == 1:
                                            try:
                                                owner.owner_vd_created_number += 1
                                                owner.save() 
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
                                                                                        vd_browser_pass =f"{fb_password}",
                                                                                        vd_owner=owner,
                                                                                        vd_description=f"created vdi by active directory users",
                                                                                        vd_browser_id=f"{fb_container['container_spec']['id']}",
                                                                                        vd_browser_img=f"{Config.DOCKER_BROWSER_IMAGE}",
                                                                                        vd_browser_name=f"{browser_name}",
                                                                                        vd_is_activate = True,
                                                                                        vd_created_by =f"LDAP-{username}",
                                                                                        vd_creator_ip=f"{creator_ip}"
                                                                                        )
                                                vdi_name=f"{vdi_name}" 
                                                vdi_url=f"{server.server_scheme}://{server.server_hostname}/{username}/"
                                                vdi_vncpass=f"{vnc_pass}"
                                                vdi_browser_url=f"{server.server_scheme}://{server.server_hostname}/{username}/fbrowser"
                                                vdi_browser_user=f"{owner.owner_user}"
                                                vdi_browser_pass=f"{vdi_model.vd_browser_pass}"
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
                                                nginx_result = update_nginx(server=server,user=f"{username}",vd_container=f"{vdi_name}",fb_container=f"{browser_name}")
                                                print(nginx_result)
                                                if int(nginx_result['result']) == 1:
                                                    return render(request, 'adAuth/info.html',context=context)
                                            except Exception as e:
                                                print(e)
                                                remove_vdi(server,user=[f"{username}"],containers=[container['container_spec']['id'],fb_container['container_spec']['id']],paths=[f"{server.data_path}/{username}-vdi"])
                                                messages.add_message(request,messages.ERROR,e)
                                                return redirect('/')
                        elif owner == None:
                            print("OWNER NONE:")
                            
                            #### create profile and vdi
                            try:
                                
                                new_profile = UserProfile.objects.create(
                        
                                    owner_name=username,
                                    owner_user=username,
                                    owner_password=password,
                                    owner_create_by_ldap=True,
                                )
                                print("NEW PROFILE:",new_profile)
                            except Exception as e :
                                print(e)
                                messages.add_message(request,messages.ERROR,'create profile error')
                                return redirect('/')
                            vdi_name = f"{username}-vdi"
                            browser_name = f"{username}-filebrowser"
                            vnc_pass = gen_password()
                            creator_ip = get_client_ip(request)
                            server = get_server()
                            container_ip = get_free_ip(server=server)
                            container = create_container(server,image=f"{Config.DOCKER_DESKTOP_IMAGE}"
                                                        ,name=f"{vdi_name}"
                                                        ,cpu='2'
                                                        ,mem='2g'
                                                        ,volumes={f"{server.data_path}/{vdi_name}/Downloads": {'bind': f"/home/{username}/Downloads", 'mode': 'rw'}}
                                                        ,env={"USER":f"{username}","PASSWORD":f"{password}aqr","VNC_PASSWORD":f"{vnc_pass}","RELATIVE_URL_ROOT":f"{username}","HTTP_PROXY":f"{username}:{password}@172.20.0.2:3128","HTTPS_PROXY":f"{username}:{password}@172.20.0.2:3128"}
                                                        ,network='no-internet'
                                                        ,ip=container_ip
                                                        )
                            print("CONTAINER",container['result'],type(container['container_spec']['ip']),container['container_spec']['ip'])
                            if int(container['result']) == 1:
                                container_fb_ip = get_free_ip(server=server)
                                vdi_id = container['container_spec']['id']
                                vdi_shortid = container['container_spec']['shortid']
                                new_profile.owner_ip = ip_pattern.search(container['container_spec']['ip'])[0]
                                new_profile.save()
                                fb_password = gen_password()
                                fb_container = create_container(server,image=f"{Config.DOCKER_BROWSER_IMAGE}"
                                                        ,name=f"{browser_name}"
                                                        ,cpu='1'
                                                        ,mem='1g'
                                                        ,volumes={f"{server.data_path}/{vdi_name}/Downloads": {'bind': f"/srv", 'mode': 'ro'}}
                                                        ,env={"FBUSER":f"{username}","FBPASSWORD":f"{fb_password}","BASEURL":f"/{username}/fbrowser"}
                                                        ,network='no-internet'
                                                        ,ip=container_fb_ip
                                                        )
                                print("FB_CONTAINER:",fb_container['result'])
                                if int(fb_container['result']) == 1:
                                    print(fb_container,fb_container['container_spec']['ip'])

                                    try:
                                        new_profile.owner_browser_ip = ip_pattern.search(fb_container['container_spec']['ip'])[0]
                                        new_profile.owner_vd_created_number += 1
                                        # new_profile.owner_updated_at = datetime.now()
                                        new_profile.save() 
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
                                                                                vd_browser_pass=f"{fb_password}",
                                                                                vd_owner=new_profile,
                                                                                vd_description=f"created vdi by active directory users",
                                                                                vd_browser_id=f"{fb_container['container_spec']['id']}",
                                                                                vd_browser_img=f"{Config.DOCKER_BROWSER_IMAGE}",
                                                                                vd_browser_name=f"{browser_name}",
                                                                                vd_is_activate = True,
                                                                                vd_created_by =f"LDAP-{username}",
                                                                                vd_creator_ip=f"{creator_ip}"
                                                                                )
                                        vdi_name=f"{vdi_name}"
                                        vdi_url=f"{server.server_scheme}://{server.server_hostname}/{username}/"
                                        vdi_vncpass=f"{vnc_pass}"
                                        vdi_browser_url=f"{server.server_scheme}://{server.server_hostname}/{username}/fbrowser"
                                        vdi_browser_user=f"{username}"
                                        vdi_browser_pass=f"{fb_password}"
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
                                        nginx_result = update_nginx(server=server,user=f"{username}",vd_container=f"{vdi_name}",fb_container=f"{browser_name}")
                                        if int(nginx_result['result']) == 1:
                                            return render(request, 'adAuth/info.html',context=context)
                                    except Exception as e:
                                        print(e,repr(e))
                                        remove_vdi(server,user=[f"{username}"],containers=[container['container_spec']['id'],fb_container['container_spec']['id']],paths=[f"{server.data_path}/{username}-vdi"])
                                        messages.add_message(request,messages.ERROR,e)
                                        return redirect('/')          
                        else:
                            messages.add_message(request,messages.ERROR,'Your Account not Activated')
                            return redirect('/')
                        
            except Exception as e:
                print(repr(e),e)
        else:
            messages.add_message(request,messages.ERROR,f"{form.errors}")
            return redirect('/')
    return redirect('/')

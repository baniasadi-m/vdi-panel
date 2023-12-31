from django.shortcuts import render,redirect,HttpResponse
from .models import VirtualDesktop,VDIServer, UserProfile
from .forms import CreateVirtualDesktop, CreateProfile
from django.db.models import Q
from django.contrib.auth.decorators import login_required,permission_required
from django.core.paginator import Paginator, EmptyPage,PageNotAnInteger,InvalidPage
from django.contrib import messages
from online_users.models import OnlineUserActivity
from vdiManager.settings import Config
from .util import *

# Main Dashboard
@login_required(login_url='/accounts/login/')
def dashboard(request):
    if status_check() == False:
        print(False)
        return redirect('/license')
    from datetime import datetime, timedelta
    today_str = datetime.today().strftime("%Y-%m-%d")
    today_obj = datetime.strptime(today_str, "%Y-%m-%d")
    last_month = today_obj.replace(month=today_obj.month -1)
    monthly_created = VirtualDesktop.objects.filter(vd_created_at__gt=datetime.date(last_month)).count()
    today_created = VirtualDesktop.objects.filter(vd_created_at__gt=datetime.date(today_obj.replace(day=today_obj.day -1))).count()
    expired = VirtualDesktop.objects.filter(vd_expired_at__lt=datetime.now()).count()
    last_7_days = today_obj + timedelta(days=-7)
    expiring = VirtualDesktop.objects.filter(Q(vd_expired_at__gt=datetime.date(last_7_days)) & Q(vd_expired_at__lt=datetime.date(today_obj))).count()
    vd_activate = VirtualDesktop.objects.filter(vd_is_activate=True).count()
    online_users = OnlineUserActivity.get_user_activities(timedelta(minutes=1)).count()

    type_counts = VDIServer.objects.all().count()
    context = {
        'online_users':online_users,
        'expired': expired,
        'activated':vd_activate,
        'expiring': expiring,
        'today_created':today_created,
        'monthly_created': monthly_created,
        'type_counts': type_counts,
        'current_datetime': get_current_datetime(),
        'current_ip':f"{get_client_ip(request)}",
    }
    return render(request, 'vdiApp/dashboard.html',context=context)

# Creating vdi container
@login_required(login_url='/accounts/login/')
def vdcreate(request):
    if status_check() == False:
        return redirect('/license')
    if user_allowed(request,usergroup=['vdadmin']):
        if request.method == 'POST':
            form=CreateVirtualDesktop(request.POST)
            if form.is_valid():
                temp_form = form.save(commit=False)
                temp_form.vd_container_cpu = request.POST['vd_container_cpu']
                temp_form.vd_container_mem = request.POST['vd_container_mem']
                temp_form.vd_container_img = Config.DOCKER_DESKTOP_IMAGE
                server_elec = get_server()
                temp_form.vd_owner.owner_server = server_elec
                try:
                    container = create_container(server=server_elec,image=f"{Config.DOCKER_DESKTOP_IMAGE}"
                                ,name=f"{temp_form.vd_owner.owner_user}-vdi"
                                ,cpu=f"{temp_form.vd_container_cpu}"
                                ,mem=f"{temp_form.vd_container_mem}"
                                ,volumes={f"{temp_form.vd_owner.owner_server.data_path}/{temp_form.vd_container_name}/Downloads": {'bind': f"/home/{temp_form.vd_container_user}/Downloads", 'mode': 'rw'}}
                                ,env={"USER":f"{temp_form.vd_container_user}","PASSWORD":f"{temp_form.vd_container_password}","VNC_PASSWORD":f"{temp_form.vd_container_vncpass}","RELATIVE_URL_ROOT":f"{temp_form.vd_owner.owner_user}","HTTP_PROXY":f"{temp_form.vd_owner.owner_user}:{temp_form.vd_owner.owner_password}@172.20.0.2:3128","HTTPS_PROXY":f"{temp_form.vd_owner.owner_user}:{temp_form.vd_owner.owner_password}@172.20.0.2:3128"}
                                ,network='no-internet'
                                ,ip=f"{temp_form.vd_owner.owner_ip}"
                                )
                    
                    if int(container['result']) == 1:
                            temp_form.vd_container_id = container['container_spec']['id']
                            temp_form.vd_container_shortid = container['container_spec']['shortid']
                            temp_form.vd_created_by = str(request.user)
                            temp_form.vd_creator_ip = get_client_ip(request)
                            temp_form.vd_browser_img = Config.DOCKER_BROWSER_IMAGE 
                            temp_form.vd_browser_name = f"{temp_form.vd_owner.owner_user}-filebrowser"
                            temp_form.vd_container_user = temp_form.vd_owner.owner_user
                            temp_form.vd_container_password = gen_password()
                            fb_password = gen_password()
                            temp_form.vd_browser_pass = fb_password
                            fb_container = create_container(server=server_elec,image=f"{Config.DOCKER_BROWSER_IMAGE}"
                                                    ,name=f"{temp_form.vd_owner.owner_user}-filebrowser"
                                                    ,cpu='1'
                                                    ,mem='1g'
                                                    ,volumes={f"{server_elec.data_path}/{temp_form.vd_owner.owner_user}-vdi/Downloads": {'bind': f"/srv", 'mode': 'ro'}}
                                                    ,env={"FBUSER":f"{temp_form.vd_owner.owner_user}","FBPASSWORD":f"{fb_password}","BASEURL":f"/{temp_form.vd_owner.owner_user}/fbrowser"}
                                                    ,network='no-internet'
                                                    ,ip=f"{temp_form.vd_owner.owner_browser_ip}"
                                                    )
                            if int(fb_container['result']) == 1:
                                temp_form.vd_browser_id = fb_container['container_spec']['id']
                                nginx_result = update_nginx(server=server_elec,user=f"{temp_form.vd_owner.owner_user}",vd_container=f"{temp_form.vd_owner.owner_user}-vdi",fb_container=f"{temp_form.vd_owner.owner_user}-filebrowser")
                                if int(nginx_result['result']) == 1:
                                    temp_form.vd_owner.owner_vd_created_number += 1
                                    temp_form.vd_expired_at = get_expiry_time()
                                    temp_form.vd_owner.save()
                                    temp_form.save()
                                    messages.add_message(request,messages.SUCCESS,'میزکار ایجاد شد')
                                    return redirect(f"/vdinfo/{temp_form.vd_container_shortid}")
                                else:
                                    messages.add_message(request,messages.ERROR,'nginx update error')
                                    return redirect('/vdcreate')          
                            else:
                                messages.add_message(request,messages.ERROR,'API Status error')
                                return redirect('/vdcreate')
                except Exception as e:
                    print(e)
                    messages.add_message(request,messages.ERROR,'API error')
                    return redirect('/vdcreate')
           

        form=CreateVirtualDesktop()
        username =request.user.get_user_permissions()
        x=request.user.groups.get(name='vdadmin')
        v=""
        print(v)
        return render(request, 'vdiApp/vdcreate.html',{'form':form,'v':v,'current_datetime': get_current_datetime(),'current_ip':f"{get_client_ip(request)}"})
    return HttpResponse("vdcreate Permission Denied")




# Remove vdi container
@login_required(login_url='/accounts/login/')
def vdremove(request,vd_id):
    vd = VirtualDesktop.objects.get(vd_container_id=vd_id)
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
            messages.add_message(request,messages.SUCCESS,'میزکار با مشخصات ذیل حذف شد')
            vd.vd_is_activate = False
            vd.save()
        else:
            messages.add_message(request,messages.WARNING,'حذف دچار مشکل شده ')

    except Exception as e:
        print(e)
        messages.add_message(request,messages.WARNING,'مشکلی در حذف رخ داده است')
        return redirect('/dashboard')

    context = {'myvd':vd,'current_datetime': get_current_datetime(),'current_ip':f"{get_client_ip(request)}"}
    return render(request, 'vdiApp/vdremove.html',context=context)
  



# list vdi container
@login_required(login_url='/accounts/login/')
def vdlist(request):
    all_entries = VirtualDesktop.objects.all()
    paginator = Paginator(all_entries,10)
    page_number = request.GET.get('page')
    try:
        vds = paginator.get_page(page_number)
    except PageNotAnInteger:
        vds = paginator.get_page(1)
    except EmptyPage:
        vds = paginator.get_page(1)
    except InvalidPage:
        vds = paginator.get_page(1)
    context = {'vds': vds,'current_datetime': get_current_datetime(),'current_ip':f"{get_client_ip(request)}"}
    return render(request, 'vdiApp/vdlist.html',context=context)

#  return HttpResponse("vdlist")


# Showing cert full info
@login_required(login_url='/accounts/login/')
def vdinfo(request,info_id):
    vd = VirtualDesktop.objects.get(vd_container_shortid=info_id)
    print(vd)
    context = {'myvd':vd,'current_datetime': get_current_datetime(),'current_ip':f"{get_client_ip(request)}"}
    return render(request, 'vdiApp/vdinfo.html',context=context)



# Showing searched vds
@login_required(login_url='/accounts/login/')
def search(request):
    search_vd = request.GET.get('q')
    if search_vd:
        vds = VirtualDesktop.objects.filter(Q(vd_owner__owner_ip=search_vd) |Q(vd_owner__owner_name=search_vd) |Q(vd_created_by__icontains=search_vd) |Q(vd_letter_number__icontains=search_vd) |Q(vd_container_name__icontains=search_vd))
    else:
        vds = VirtualDesktop.objects.all().order_by("-vd_created_at")
    context = {'vds': vds,'current_datetime': get_current_datetime(),'current_ip':f"{get_client_ip(request)}"}
    return render(request, 'vdiApp/search.html',context=context)

# Showing list of servers
@login_required(login_url='/accounts/login/')
def serverlist(request):
    all_entries = VDIServer.objects.all()
    paginator = Paginator(all_entries,10)
    page_number = request.GET.get('page')
    try:
        servers = paginator.get_page(page_number)
    except PageNotAnInteger:
        servers = paginator.get_page(1)
    except EmptyPage:
        servers = paginator.get_page(1)
    except InvalidPage:
        servers = paginator.get_page(1)
    context = {'servers': servers,'current_datetime': get_current_datetime(),'current_ip':f"{get_client_ip(request)}"}
    return render(request, 'vdiApp/serverlist.html',context=context)



# Showing server status and info
@login_required(login_url='/accounts/login/')
def server_info(request,info_id):
    server = VDIServer.objects.get(server_name=info_id)
    url = f"{server.server_scheme}://{server.server_ip}:{server.server_port}/api/v1/load"
    if server_status(server_url=url) == True:
        messages.add_message(request,messages.SUCCESS,'VDI Agent Status is Running')
    else:
        messages.add_message(request,messages.WARNING,'VDI Agent Status is Unknown ')

    context = {'server': server,'current_datetime': get_current_datetime(),'current_ip':f"{get_client_ip(request)}"}
    return render(request, 'vdiApp/serverinfo.html',context=context)

# Remove profile
@login_required(login_url='/accounts/login/')
def profile_remove(request,profile_id):
    print(profile_id)
    try:
        profile = UserProfile.objects.get(owner_user=profile_id)
        data = {
            "username" : f"{profile.owner_user}",
            "password" : f"{profile.owner_password}"
        }
        headers={'Content-Type': 'application/json'}
        jwt_token = jwt_gen_token()
        headers.update(
            {
                'jwt': f"{jwt_token}"
            }
        )
        server = profile.owner_server
        import requests,json
        
        url = f"{server.server_scheme}://{server.server_ip}:{server.server_port}/api/v1/squidupdate"
        requests.delete(url=url,headers=headers,data=json.dumps(data),verify=False).json()

        vd = VirtualDesktop.objects.get(vd_owner=profile,vd_is_activate=True)
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
            r = requests.delete(url=url,headers=headers,data=json.dumps(data),verify=False).json()
            if int(r['status']) == 1:
                profile.delete()
                context = {'profile':profile,'current_datetime': get_current_datetime(),'current_ip':f"{get_client_ip(request)}"}
                messages.add_message(request,messages.SUCCESS,'پروفایل با مشخصات ذیل حذف شد')
                return render(request, 'vdiApp/profileremove.html',context=context)

            else:
                messages.add_message(request,messages.WARNING,'حذف میزکار دچار مشکل شده ')
                return redirect('/dashboard')

        except Exception as e:
            print(e)
            messages.add_message(request,messages.WARNING,'مشکلی در حذف میزکار  رخ داده است')
            return redirect('/dashboard')
     
    except Exception as e:
        print(e)
        messages.add_message(request,messages.WARNING,'مشکلی در حذف پروفایل رخ داده است')
        return redirect('/dashboard')
    
@login_required(login_url='/accounts/login/')
def profile_create(request):
    if user_allowed(request,usergroup=['vdadmin']):
        if request.method == 'POST':
            form=CreateProfile(request.POST)
            print("PROFILE")
            if form.is_valid():
                tmp_form = form.save(commit=False)
                print(tmp_form)
                server = tmp_form.owner_server
                # print(server)
                container_ip = get_free_ip(server=server)
                # print(container_ip)
                if container_ip == False:
                    return HttpResponse("free ip error")
                print(container_ip)

                import re 
                ip_pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
                container1 = create_container(server,image=f"{Config.DOCKER_BROWSER_IMAGE}"
                                            ,name=f"temp_container1"
                                            ,cpu='1'
                                            ,mem='1g'
                                            ,network='no-internet'
                                            ,volumes={f"{server.data_path}/temp1/Downloads": {'bind': f"/srv", 'mode': 'rw'}}
                                            ,env={"FBUSER":f"fgddf","FBPASSWORD":f"sdffdfs","BASEURL":f"/sdasdsa/fbrowser"}
                                            ,ip=container_ip)
                print(container1)
                
                tmp_form.owner_ip = ip_pattern.search(container1['container_spec']['ip'])[0]
                container_ip = get_free_ip(server=server)
                if container_ip == False:
                    return HttpResponse("free ip error")
                container2 = create_container(server,image=f"{Config.DOCKER_BROWSER_IMAGE}"
                                            ,name=f"temp_container2"
                                            ,cpu='1'
                                            ,mem='1g'
                                            ,network='no-internet'
                                            ,volumes={f"{server.data_path}/temp1/Downloads": {'bind': f"/srv", 'mode': 'rw'}}
                                            ,env={"FBUSER":f"fgddf","FBPASSWORD":f"sdffdfs","BASEURL":f"/sdasdsa/fbrowser"}
                                            ,ip=container_ip
                                            )
                # data_paths = []
                # data_paths.append
                tmp_form.owner_browser_ip = ip_pattern.search(container2['container_spec']['ip'])[0]
                import requests,json
                url = f"{server.server_scheme}://{server.server_ip}:{server.server_port}/api/v1/containers"
                try:
                    containers_ids = []
                    containers_ids.append(container1['container_spec']['id'])
                    containers_ids.append(container2['container_spec']['id'])
                    data = {'path':list([1]),'ids': list([2]),'user':'jjjj'}
                    headers={'Content-Type': 'application/json'}
                    jwt_token = jwt_gen_token()
                    headers.update(
                        {
                            'jwt': f"{jwt_token}"
                        }
                    )

                    for i in containers_ids:
                        new_url = url + f"/{i}"
                        print(new_url)
                        r = requests.delete(url=new_url,headers=headers,verify=False).json()
                        print(r)
                    data = {
                        "username" : f"{tmp_form.owner_user}",
                        "password" : f"{tmp_form.owner_password}"
                    }
                    print(data)
                    url = f"{server.server_scheme}://{server.server_ip}:{server.server_port}/api/v1/squidupdate"
                    print(url)
                    # r  = requests.post(url=url,headers=headers,data=json.dumps(data),verify=False).json()
                    print(url, r)
                    r = {
                        'status' : '1'
                     } 
                    if int(r['status']) == 1 :
                        tmp_form.save()
                        messages.add_message(request,messages.SUCCESS,'پروفایل ایجاد شد')
                        return redirect(f"/profileinfo/{tmp_form.owner_user}")    
                    else:

                        messages.add_message(request,messages.WARNING,'خطا در ایجاد پروفایل')
                except Exception as e:
                    print("exception",e)    
        form=CreateProfile()
        v=""
        print(v)
        return render(request, 'vdiApp/profilecreate.html',{'form':form,'v':v,'current_datetime': get_current_datetime(),'current_ip':f"{get_client_ip(request)}"})
       
    return HttpResponse("vdcreate Permission Denied")        
@login_required(login_url='/accounts/login/')
def profile_list(request):
    if user_allowed(request,usergroup=['vdadmin']):
        all_entries = UserProfile.objects.all()
        paginator = Paginator(all_entries,10)
        page_number = request.GET.get('page')
        try:
            vds = paginator.get_page(page_number)
        except PageNotAnInteger:
            vds = paginator.get_page(1)
        except EmptyPage:
            vds = paginator.get_page(1)
        except InvalidPage:
            vds = paginator.get_page(1)
        context = {'profiles': vds,'current_datetime': get_current_datetime(),'current_ip':f"{get_client_ip(request)}"}
        return render(request, 'vdiApp/profilelist.html',context=context)

@login_required(login_url='/accounts/login/')
def profile_info(request,info_id):
    if user_allowed(request,usergroup=['vdadmin']):
        try:
            profile = UserProfile.objects.get(owner_user=info_id)
        except Exception as e:
            print(f"profile info exception: {e}")
            messages.add_message(request,messages.WARNING,'خطا در دریافت اطلاعات کاربری')
            return redirect('/profilelist')
        try:
            vd = VirtualDesktop.objects.get(vd_owner= profile,vd_is_activate=True)
        except VirtualDesktop.DoesNotExist:
            vd = None
        print(vd)
        context = {'profile':profile,'current_datetime': get_current_datetime(),'current_ip':f"{get_client_ip(request)}"}
        if vd != None:
            vd_url = f"{vd.vd_owner.owner_server.server_scheme}://{vd.vd_owner.owner_server.server_hostname}/{profile.owner_user}/"
            vd_vnc_pass = vd.vd_container_vncpass
            context.update(
                {
                    'vd_url': vd_url,
                    'vd_vnc_pass': vd_vnc_pass
                }
            )
        return  render(request,'vdiApp/profileinfo.html',context=context)

@login_required(login_url='/accounts/login/')
def profile_edit(request,profile_id= None):
    if user_allowed(request,usergroup=['vdadmin']):
        if profile_id == None:
            all_entries = UserProfile.objects.all()
            paginator = Paginator(all_entries,10)
            page_number = request.GET.get('page')
            try:
                vds = paginator.get_page(page_number)
            except PageNotAnInteger:
                vds = paginator.get_page(1)
            except EmptyPage:
                vds = paginator.get_page(1)
            except InvalidPage:
                vds = paginator.get_page(1)
            context = {'profiles': vds,'current_datetime': get_current_datetime(),'current_ip':f"{get_client_ip(request)}"}
            return render(request, 'vdiApp/profileeditlist.html',context=context)
       
        else:
            try:
                profile = UserProfile.objects.get(owner_user=profile_id)
                
            except Exception as e:
                print(f"profile info exception: {e}")
                messages.add_message(request,messages.WARNING,'خطا در دریافت اطلاعات کاربر')
                return redirect('/profilelist')

            
            if request.method == 'POST':
                print(request.POST)
                form = CreateProfile(request.POST, instance=profile)
                tmp_form = form.save(commit=False)
                if 'owner_is_active' in request.POST:
                    tmp_form.owner_is_active =True
                else:
                    tmp_form.owner_is_active =False
                if 'owner_create_by_ldap' in request.POST:
                    tmp_form.owner_create_by_ldap =True
                else:
                    tmp_form.owner_create_by_ldap =False 
                messages.add_message(request,messages.SUCCESS,' اطلاعات کاربر بروزرسانی شد')   
                tmp_form.save()
                return redirect('/profilelist')

            form =  CreateProfile(instance=profile)
            context = {'form':form,'profile_id':profile.owner_user,'current_datetime': get_current_datetime(),'current_ip':f"{get_client_ip(request)}"}
            
            return  render(request,'vdiApp/profileedit.html',context=context)




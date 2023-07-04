from django.shortcuts import render,redirect,HttpResponse
from .models import VirtualDesktop,VDIServer
from .forms import CreateVirtualDesktop
from django.db.models import Q
from django.contrib.auth.decorators import login_required,permission_required
from django.core.paginator import Paginator, EmptyPage,PageNotAnInteger,InvalidPage
from django.contrib import messages
from online_users.models import OnlineUserActivity
from vdiManager.settings import Config
from .util import get_client_ip, get_current_datetime, get_server, user_allowed, server_status

# Main Dashboard
@login_required(login_url='/accounts/login/')
def dashboard(request):
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
    if user_allowed(request,usergroup=['vdadmin']):
        if request.method == 'POST':
            form=CreateVirtualDesktop(request.POST)
            if form.is_valid():
                temp_form = form.save(commit=False)
                temp_form.vd_container_cpu = request.POST['vd_container_cpu']
                temp_form.vd_container_mem = request.POST['vd_container_mem']
                temp_form.vd_container_img = Config.DOCKER_DESKTOP_IMAGE
                server_elec = get_server()
                temp_form.vd_server = server_elec
                # temp_form.vd_server.server_ip = get_server()
                url = f"{temp_form.vd_server.server_scheme}://{temp_form.vd_server.server_ip}:{temp_form.vd_server.server_port}/api/v1/containers"
                headers={'Content-Type': 'application/json'}
                data = {
                        'image': f"{temp_form.vd_container_img}",
                        'name' : f"{temp_form.vd_container_name}",
                        'cpu' : f"{temp_form.vd_container_cpu}",
                        'mem' : f"{temp_form.vd_container_mem}",
                        'volumes' : {f"{temp_form.vd_server.data_path}/{temp_form.vd_container_name}/Downloads": {'bind': f"/home/{temp_form.vd_container_user}/Downloads", 'mode': 'rw'}},
                        'env' : {"USER":f"{temp_form.vd_container_user}","PASSWORD":f"{temp_form.vd_container_password}","VNC_PASSWORD":f"{temp_form.vd_container_vncpass}"},
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

                    # r={'status':'1','container_spec':{'id':"dfcddevfervervvr",'short_id':"fvdfdre"}}
                    
                    if int(r['status']) == 1:
                        temp_form.vd_container_id = r['container_spec']['id']
                        temp_form.vd_container_shortid = r['container_spec']['short_id']
                        temp_form.vd_created_by = str(request.user)
                        temp_form.vd_creator_ip = get_client_ip(request)
                        temp_form.vd_browser_img = Config.DOCKER_BROWSER_IMAGE 
                        temp_form.vd_browser_name = temp_form.vd_container_name + '-filebrowser'
                        data = {
                                'image': f"{temp_form.vd_browser_img}",
                                'name' : f"{temp_form.vd_browser_name}",
                                'cpu' : "2",
                                'mem' : "1g",
                                'volumes' : {f"{temp_form.vd_server.data_path}/{temp_form.vd_container_name}/Downloads": {'bind': f"/srv", 'mode': 'ro'}},
                                'env' : {"USER":"vdi"},
                                'ports' : ['80'],
                                # 'ports' : {'80/tcp':int(f"{temp_form.vd_browser_port}")},
                                }
                        r = requests.post(url=url,data=json.dumps(data),headers=headers,verify=False).json()
                        print(r)
                        if int(r['status']) == 1:
                            temp_form.vd_browser_id = r['container_spec']['id']
                            response_ports = json.loads(r['container_spec']['host_ports'])
                            if len(response_ports) > 1:
                                for i in response_ports:
                                    temp_form.vd_browser_port += f",{str(i)}"
                            else:
                                temp_form.vd_browser_port = response_ports[0]
                            temp_form.save()
                            messages.add_message(request,messages.SUCCESS,'میزکار ایجاد شد')
                            return redirect(f"/vdinfo/{temp_form.vd_container_shortid}")
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
    data_paths.append(f"{vd.vd_server.data_path}/{vd.vd_container_name}")
    import requests,json
    url = f"{vd.vd_server.server_scheme}://{vd.vd_server.server_ip}:{vd.vd_server.server_port}/api/v1/containers"
    try:
        data = {'path':list(data_paths),'ids': list(container_ids)}
        headers={'Content-Type': 'application/json'}
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
        vds = VirtualDesktop.objects.filter(Q(vd_created_by__icontains=search_vd) |Q(vd_letter_number__icontains=search_vd) |Q(vd_owner__icontains=search_vd) |Q(vd_container_name__icontains=search_vd))
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

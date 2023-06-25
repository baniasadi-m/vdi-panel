from django.shortcuts import render,redirect,HttpResponse
from .models import VirtualDesktop,VDIServer
from django.db.models import Q
from django.contrib.auth.decorators import login_required,permission_required
from django.core.paginator import Paginator, EmptyPage,PageNotAnInteger,InvalidPage
from django.contrib.auth.models import User, Group,Permission
from django.contrib import messages
import os
from django.conf import settings
from django.http import FileResponse
from online_users.models import OnlineUserActivity


from datetime import datetime

def get_current_datetime():
    return datetime.now()
  
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


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
    cert_activate = VirtualDesktop.objects.filter(vd_is_activate=True).count()
    online_users = OnlineUserActivity.get_user_activities(timedelta(minutes=1)).count()

    type_counts = VDIServer.objects.all().count()
    context = {
        'online_users':online_users,
        'expired': expired,
        'activated':cert_activate,
        'expiring': expiring,
        'today_created':today_created,
        'monthly_created': monthly_created,
        'type_counts': type_counts,
        'current_datetime': get_current_datetime(),
        'current_ip':f"{get_client_ip(request)}",
    }
    return render(request, 'vdiApp/dashboard.html',context=context)

# Showing searched certs
@login_required(login_url='/accounts/login/')
def search(request):
    search_cert = request.GET.get('q')
    if search_cert:
        certs = VirtualDesktop.objects.filter(Q(cert_user_national_id__icontains=search_cert) |Q(cert_user_family__icontains=search_cert) |Q(cert_letter_number__icontains=search_cert))
    else:
        certs = VirtualDesktop.objects.all().order_by("-vd_created_at")
    context = {'certs': certs,'current_datetime': get_current_datetime(),'current_ip':f"{get_client_ip(request)}"}
    return render(request, 'vdiApp/search.html',context=context)
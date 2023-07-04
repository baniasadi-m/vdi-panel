from django.urls import path, include
from .views import *

app_name = 'vdiApp'
urlpatterns = [
    path('dashboard/',dashboard , name='dashboard'),
    path('search/',search , name='search'), 
    path('vdcreate/',vdcreate , name='vdcreate'), 
    path('vdlist/',vdlist , name='vdlist'), 
    path('vdremove/<vd_id>',vdremove , name='vdremove'), 
    path('vdinfo/<info_id>',vdinfo , name='vdinfo'),
    path('serverlist/',serverlist , name='serverlist'),
    path('serverinfo/<info_id>',server_info , name='serverinfo'),
    path('api/v1/',include('vdiApp.api.v1.urls')),
]
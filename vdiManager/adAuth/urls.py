from django.urls import path
from .views import adauth_get_info,adauth_list_info

app_name = 'adAuth'
urlpatterns = [
    path('',adauth_get_info , name='getinfo'),
    path('authinfo/',adauth_list_info , name='listinfo'),

]
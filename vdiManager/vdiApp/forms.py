from django import forms
from .models import VirtualDesktop,UserProfile

cpu_choices =[
    ('2','2 core'),
    ('4','4 core'),
]

mem_choices =[
    ('2g','2GB'),
    ('4g','4GB'),
]

class CreateVirtualDesktop(forms.ModelForm):
    class Meta:
        model = VirtualDesktop
        fields = ['vd_container_name','vd_container_vncpass',
        'vd_owner','vd_letter_number','vd_description'
        ]
    vd_container_cpu = forms.ChoiceField(choices=cpu_choices,label='پردازنده')
    vd_container_mem = forms.ChoiceField(choices=mem_choices,label='حافظه')
 
class CreateProfile(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['owner_name','owner_user','owner_password','owner_server','owner_description','owner_create_by_ldap','owner_is_active']
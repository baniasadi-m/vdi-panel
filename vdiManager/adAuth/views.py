from django.shortcuts import render,HttpResponse
from vdiApp.util import ad_auth_user
from vdiApp.config import Config
# Create your views here.
def adauth_get_info(request):
    context ={}
    return render(request, 'adAuth/adinput.html',context=context)
    
def adauth_list_info(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        myuser = ad_auth_user(server_ip="",username= username, password= password,domain=Config.Active_Directory_DomainName)

        

        if myuser is not None:
            return HttpResponse('login')
        else:
            return HttpResponse('not login')


  
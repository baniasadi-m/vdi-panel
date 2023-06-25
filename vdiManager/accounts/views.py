from django.shortcuts import render,redirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.core import  cache

# Create your views here.

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        myuser = authenticate(request,username= username, password= password)

        

        if myuser is not None:
            login(request,myuser)
            if request.POST['next']:
                return redirect(request.POST['next'])
            return redirect('/')
        else:
            return HttpResponse('not login')

    return render(request, 'accounts/login.html')
def logout_view(request):
    logout(request)
    return redirect('/accounts/login')
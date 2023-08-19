from datetime import datetime
from .models import VDIServer,VirtualDesktop,UserProfile
import ldap3
from ldap3 import Server, Connection, SUBTREE
from vdiManager.settings import Config
import random
import string

from jwt import encode
import time

def jwt_gen_token():
    current_time = int(time.time())
    payload ={
        "iss": f"{Config.AGENT_JWT_ISSUER}",
        "iat": current_time - 60,
        "exp": current_time + 60,
        "nbf": current_time - 3600,
    }
    secret = Config.AGENT_JWT_SECRET

    return encode(payload,secret,Config.AGENT_JWT_ALGO)


def gen_password(length=12):

    ''' generates a random password '''
    return ''.join(
        random.choices(
            string.ascii_lowercase + string.digits,
            k=length
        )
    )

def ad_auth_user(server_ip,username, password,domain):
    server = ldap3.Server(f"ldap://{server_ip}")
    try:
        with ldap3.Connection(server, user=f"{username}@{domain}", password=password, auto_bind=True) as conn:
            # Check that the user is a member of a particular group
            if conn.search('OU={},DC={},DC={}'.format(Config.Active_Directory_OUName,domain.split('.')[0],domain.split('.')[1]), '(sAMAccountName={})'.format(username), attributes=['memberOf']):
                return True,conn.search
            else:
                return False,conn.search
    except ldap3.core.exceptions.LDAPException as e:
        print('LDAP authentication failed: {}'.format(e))
        return False,e

def getUsersInGroup(server_ip,username, password,domain,group):
    # SearchBase= f"DC={domain.split('.')[0]},DC={domain.split('.')[1]}"
    SearchBase= "DC=" + domain.replace(".", ",DC=")
    server = Server(server_ip)
    # print(server)
    try:
        conn = Connection(server, user=username, password=password, auto_bind=True)
        # print(conn)
        conn.bind()
        filter =f"(&(objectClass=GROUP)(cn={group}))"
        ad_exists = conn.search(search_base=SearchBase,
                    search_filter=filter, search_scope=SUBTREE,
                    attributes=['member'], size_limit=0)
        print(ad_exists)
        if ad_exists:
            #result = conn.entries
            result = conn.response_to_json()
            conn.unbind() 
            return True,result
        else:
            return False,result
    except ldap3.core.exceptions.LDAPException as e:
        print('LDAP authentication failed: {}'.format(e))
        return False,e
    
def get_server():
    import requests
    min_load = 500.00
    servers = VDIServer.objects.all()
    # print(type(servers),servers)
    headers={'Content-Type': 'application/json'}
    jwt_token = jwt_gen_token()
    headers.update(
        {
            'jwt': f"{jwt_token}"
        }
    )
    url=""
    final_server_id = ""
    for server in servers:
        # print(server.id,type(server))
        url = f"{server.server_scheme}://{server.server_ip}:{server.server_port}/api/v1/load"
        try:
            result = requests.get(url=url,headers=headers,verify=False).json()
            if float(result['load']) < min_load:
                min_load = int(result['load'])
                final_server_id = server.id
        except Exception as e:
            continue
    final_server = VDIServer.objects.get(id=final_server_id)
    # print(final_server,final_server_id,min_load)
    return final_server

def get_current_datetime():
    return datetime.now()
  
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_free_ip(server):
    import requests
    headers={'Content-Type': 'application/json'}
    url = f"{server.server_scheme}://{server.server_ip}:{server.server_port}/api/v1/getip"
    jwt_token = jwt_gen_token()
    headers.update(
        {
            'jwt': f"{jwt_token}"
        }
    )
    try:
        r = requests.get(url=url,headers=headers,verify=False,timeout=20).json()
        print(r)
        if int(r['result']) == 1:
            return r['free_ip']
    except Exception as e:
        print(e)
        return False
    
def user_allowed(request,usergroup=[]):
    for g in usergroup:
        if request.user.groups.filter(name=f"{g}").exists():
            return True
    return False

def server_status(server_url):
    import requests
    headers={'Content-Type': 'application/json'}
    jwt_token = jwt_gen_token()
    headers.update(
        {
            'jwt': f"{jwt_token}"
        }
    )
    try:
        r = requests.get(url=server_url,headers=headers,verify=False,timeout=2).json()
        if int(r['status']) == 1:
            return True
    except Exception as e:
        print(e)
        return False
    


def create_container(server,image,name,cpu,mem,volumes,env,network=None,ip=None):
    import requests, json
    url = f"{server.server_scheme}://{server.server_ip}:{server.server_port}/api/v1/containers"
    headers={'Content-Type': 'application/json'}
    jwt_token = jwt_gen_token()
    headers.update({
        'jwt':f"{jwt_token}"
    })
    result = {}
    if network == None and ip == None:
        data = {
                'image': f"{image}",
                'name' : f"{name}",
                'cpu' : f"{cpu}",
                'mem' : f"{mem}",
                'volumes' : volumes,
                'env' : env,
                }

    else:
                data = {
                'image': f"{image}",
                'name' : f"{name}",
                'cpu' : f"{cpu}",
                'mem' : f"{mem}",
                'volumes' : volumes,
                'env' : env,
                'network' : network,
                'ip' : ip,
                }

    try:
        r = requests.post(url=url,data=json.dumps(data),headers=headers,verify=False).json()
        if int(r['status']) == 1:
            container_id = r['container_spec']['id']
            container_shortid = r['container_spec']['short_id']
            container_name = r['container_spec']['name']
            container_status = r['container_spec']['status']
            container_ip = r['container_spec']['ips']

            result.update(
                {
                    'container_spec':{
                        'id': container_id,
                        'shortid': container_shortid,
                        'name': container_name,
                        'id': container_id,
                        'status': container_status,
                        'ip': container_ip,
                    },
                    'result':f"{r['status']}"

                }
            )
            return result
        result.update(
            {
               'result':f"{r['status']}"
            }
        )
        return 
        
    except Exception as e:
        print(e)

def update_nginx(server,user,vd_container,fb_container):
    import requests, json
    url = f"{server.server_scheme}://{server.server_ip}:{server.server_port}/api/v1/nginxupdate"
    headers={'Content-Type': 'application/json'}
    jwt_token = jwt_gen_token()
    headers.update({
        'jwt':f"{jwt_token}"
    })
    result = {}

    data = {
            'user': f"{user}",
            'vd_container' : f"{vd_container}",
            'fb_container' : f"{fb_container}",
 
            }


    try:
        r = requests.post(url=url,data=json.dumps(data),headers=headers,verify=False).json()
        if int(r['status']) == 1:
            result.update(
                {
                    "msg":"nginx updated",

                    'result':f"{r['status']}"

                }
            )
            return result
        result.update(
            {
               'result':f"{r['status']}"
            }
        )
        return 
        
    except Exception as e:
        print(e)

from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

def get_vd_or_None(container_user,is_activate):
    try:
        # obj = VirtualDesktop.objects.filter(Q(vd_container_user__iexact=container_user) & Q(vd_is_activate__iexact=is_activate)).first()
        obj = VirtualDesktop.objects.get(vd_container_user=container_user,vd_is_activate=is_activate)
        if obj:
            print(obj)
            print(obj.vd_is_activate)
        return obj
    except ObjectDoesNotExist:
        return None
    
def get_profile_or_None(user,password):
    try:
        # obj = UserProfile.objects.filter(Q(owner_user__iexact=user) & Q(owner_password__iexact=password)).first()
        obj = UserProfile.objects.get(owner_user=user, owner_password=password)
        # if obj :
        #     print(obj)
            
        return obj
    except ObjectDoesNotExist:
        return None
    
def profile_update_password(username,password):
    try:
        obj = UserProfile.objects.get(owner_user=username)
        obj.owner_password = password
        obj.save()
        return True
    except ObjectDoesNotExist:
        print("NO PROFILE TO UPDATE")


def remove_vdi(server,user=[],containers=[],paths=[]):

    import requests,json
    url = f"{server.server_scheme}://{server.server_ip}:{server.server_port}/api/v1/containers"
    try:
        data = {'path':list(paths),'ids': list(containers),'user': user}
        headers={'Content-Type': 'application/json'}
        jwt_token = jwt_gen_token()
        headers.update(
            {
                'jwt': f"{jwt_token}"
            }
        )
        r = requests.delete(url=url,headers=headers,data=json.dumps(data),verify=False).json()
        if int(r['status']) == 1:
            return True
        return False
    except Exception as e:
        print("Remove Vdi Exception:",e)
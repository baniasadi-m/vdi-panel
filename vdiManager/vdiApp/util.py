from datetime import datetime
from .models import VDIServer
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
    SearchBase= f"DC={domain.split('.')[0]},DC={domain.split('.')[1]}"
    server = Server(server_ip)
    try:
        conn = Connection(server, user=username, password=password, auto_bind=True)
        conn.bind()
        if conn.search(search_base=SearchBase,
                    search_filter='(&(objectClass=GROUP)(cn=' + group +'))', search_scope=SUBTREE,
                    attributes=['member'], size_limit=0):
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

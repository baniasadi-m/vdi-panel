from datetime import datetime
from .models import VDIServer
import ldap3
from .config import Config

def ad_auth_user(server_ip,username, password,domain):
    server = ldap3.Server(f"ldap://{server_ip}")
    try:
        with ldap3.Connection(server, user=f"{username}@{domain}", password=password, auto_bind=True) as conn:
            # Check that the user is a member of a particular group
            if conn.search('OU={},DC={},DC={}'.format(Config.Active_Directory_OUName,domain.split('.')[0],Config.Active_Directory_DomainName.split('.')[1]), '(sAMAccountName={})'.format(username), attributes=['memberOf']):
                return True
            else:
                return False
    except ldap3.core.exceptions.LDAPException as e:
        print('LDAP authentication failed: {}'.format(e))
        return False

def get_server():
    import requests
    min_load = 500.00
    servers = VDIServer.objects.all()
    # print(type(servers),servers)
    headers={'Content-Type': 'application/json'}
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
    try:
        r = requests.get(url=server_url,headers=headers,verify=False,timeout=2).json()
        if int(r['status']) == 1:
            return True
    except Exception as e:
        print(e)
        return False

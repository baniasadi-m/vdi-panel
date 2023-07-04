import ldap3

def ad_auth_user(server_ip,username, password,domain):
    server = ldap3.Server(f"ldap://{server_ip}")
    try:
        with ldap3.Connection(server, user=f"{username}@{domain}", password=password, auto_bind=True) as conn:
            # Check that the user is a member of a particular group
            if conn.search('OU={},DC={},DC={}'.format("MYVDI",domain.split('.')[0],domain.split('.')[1]), '(sAMAccountName={})'.format(username), attributes=['memberOf']):
                #print(conn.search('OU={},DC={},DC={}'.format("MYVDI",domain.split('.')[0],domain.split('.')[1]), '(sAMAccountName={})'.format(username), attributes=['memberOf']))
                #print(conn.result)
                return True,conn.result
            else:
                return False,conn.result
    except ldap3.core.exceptions.LDAPException as e:
        #print('LDAP authentication failed: {}'.format(e))
        return False,e
r=ad_auth_user(server_ip="192.168.122.45",username="masoud", password="a123qwe!",domain="masoud.com")

print(r)

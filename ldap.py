import ldap3

server = ldap3.Server("ldap://",get_info=ldap3.ALL)
conn = ldap3.Connection(server,'cn=admin,dc=nodomain','admin')
print(conn)
print(conn.bind())

conn.extend.standard.who_am_i()

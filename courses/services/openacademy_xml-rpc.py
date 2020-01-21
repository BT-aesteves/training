import xmlrpc.client

class Conection():

    HOST = "localhost"
    PORT = 8069
    DB = "test"
    USER = "admin@odoo.com"
    PASS = "123456"

    def create_session(HOST, PORT, USER, PASS, DB):

        root = 'http://%s:%d/xmlrpc/' % (HOST, PORT)
        uid = xmlrpc.client.ServerProxy(root + 'common').login(DB, USER, PASS)
        sock = xmlrpc.client.ServerProxy(root + 'object')
        args = {'name': 'Testing'}
        print(sock.execute(DB, uid, PASS, 'session', 'create', args))

    create_session(HOST, PORT, USER, PASS, DB)



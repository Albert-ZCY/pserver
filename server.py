from socket import *
import sys
import os
import json
import threading
import sys

sys.stderr = open('error.log', 'a')
sys.stdout = open('output.log', 'a')

host = '192.168.3.224'
port = 8000

try:
    s = socket(AF_INET, SOCK_STREAM)
    s.bind((host, port))
    s.listen(10)
except error as msg:
    print(msg)
    sys.exit()
finally:
    print('Server created successfully.')

class Deal():
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        print(f'{self.addr} connectted to this server.')
        self.cfpath = f'dynamic{os.sep}info.json'
        self.char = conn.recv(1024).decode()
        self.data = self.char.strip().split(' ')
        self.model = {'type': '', 'content': '', 'value': 0}
        self.main()
        self.conn.close()

    def main(self):
        command = self.data[0]

        if command == 'signin':
            self.signin()
        elif command == 'register':
            self.register()
        elif command == 'cancel':
            self.cancel()
        else:
            reply = self.model
            reply['type'] = 'error'
            reply['content'] = 'Invalid command.'
            reply['value'] = 0
            text = json.dumps(reply)
            self.conn.sendall(text.encode())

    def readInfo(self, key):
        with open(self.cfpath, 'r') as config:
            content = json.load(config)
            return content.get(key)

    def writeInfo(self, key, value):
        with open(self.cfpath, 'r+') as config:
            content = json.load(config)
            content[key] = value
            config.seek(0)
            config.truncate()
            json.dump(content, config)

    def signin(self):
        id = self.data[1]
        lockedpsw = self.data[2]  # Encrypted password by MD5

        if os.path.exists('client'+os.sep+str(id)+'.json'):
            with open('client'+os.sep+str(id)+'.json', 'r') as config:
                content = json.load(config)
                if content['pswmd5'] == lockedpsw:
                    reply = self.model
                    reply['type'] = 'reply'
                    reply['content'] = 'Allow to sign in.'
                    reply['value'] = content['username']
                    text = json.dumps(reply)
                    self.conn.sendall(text.encode())
                else:
                    reply = self.model
                    reply['type'] = 'reply'
                    reply['content'] = 'Disallow to sign in : password error.'
                    reply['value'] = 0
                    text = json.dumps(reply)
                    self.conn.sendall(text.encode())
        else:
            reply = self.model
            reply['type'] = 'reply'
            reply['content'] = 'Disallow to sign in : id error.'
            reply['value'] = 0
            text = json.dumps(reply)
            self.conn.sendall(text.encode())
        print(f'replyed {self.addr} with message: {text}.')
        
        
    def register(self):
        username = self.data[1]
        lockedpsw = self.data[2]  # Encrypted password by MD5
        id = self.readInfo('number') + 1
        self.writeInfo('number', id)

        with open('client'+os.sep+str(id)+'.json', 'w') as config:
            content = {"id":id, "username":username, 'pswmd5':lockedpsw}
            json.dump(content, config)

        os.mkdir('service'+os.sep+str(id))

        reply = self.model
        reply['type'] = 'reply'
        reply['content'] = 'Registered successfully.'
        reply['value'] = id
        text = json.dumps(reply)
        self.conn.sendall(text.encode())

        print(f'replyed {self.addr} with message: {text}.')

    def cancel(self):
        id = self.data[1]
        lockedpsw = self.data[2]

        if os.path.exists('client'+os.sep+str(id)+'.json'):
            with open('client'+os.sep+str(id)+'.json', 'r') as config:
                content = json.load(config)
                if content['pswmd5'] == lockedpsw:
                    config.close()
                    os.remove('client'+os.sep+str(id)+'.json')
                    os.rmdir('service'+os.sep+str(id))
                    reply = self.model
                    reply['type'] = 'reply'
                    reply['content'] = 'Canceled successfully.'
                    reply['value'] = 1
                    text = json.dumps(reply)
                    self.conn.sendall(text.encode())
                else:
                    reply = self.model
                    reply['type'] = 'reply'
                    reply['content'] = 'Disallow to cancel : password error.'
                    reply['value'] = 0
                    text = json.dumps(reply)
                    self.conn.sendall(text.encode())
        else:
            reply = self.model
            reply['type'] = 'reply'
            reply['content'] = 'Disallow to cancel : id error.'
            reply['value'] = 0
            text = json.dumps(reply)
            self.conn.sendall(text.encode())
        print(f'replyed {self.addr} with message: {text}.')

while True:
    conn, addr = s.accept()
    thread = threading.Thread(target=Deal, args=(conn, addr))
    thread.start()

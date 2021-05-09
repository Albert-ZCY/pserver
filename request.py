# Request Example
from socket import *
from hashlib import *
import sys
import time
import json

host = '192.168.3.224'
port = 8000

try:
    s = socket(AF_INET, SOCK_STREAM)
    s.connect((host, port))
except error as msg:
    print(msg)
    sys.exit(0)
print('Client side connected successfully.')

psw = new('md5', b'pointcode2021').hexdigest()
msg = 'register '+'PointCode '+str(psw)
s.sendall(msg.encode())
time.sleep(1)
reply = s.recv(1024).decode()
data = json.loads(reply)
print(data)
#import sys
import selectors
#import types
import socket

HOST = '127.0.0.1' # localhost
PORT = 65432 # Port to listen on
import threading
socket_list = []
s = socket.socket()
s.bind(('127.0.0.1', 8001))
s.listen()

def socket_target(conn):
    while True:
        data = conn.recv(1024)
        if not data:
            break
        conn.send(data)

while True:
    conn, address = s.accept()
    socket_list.append(conn)
    threading.Thread(target = socket_target, args = (ConnectionRefusedError,)).start
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
    while True:
        data = conn.recv(1024)
        if not data:
            break
        conn.sendall(data)
s.close()

sel = selectors.DefaultSelector()
HOST = "127.0.0.1"
PORT = 1024
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST,PORT))
    s.listen()
    print(f"Listening on {(HOST, PORT)}")
    s.setblocking(False)
    sel.register(s, selectors.EVENT_READ, data=None)
    
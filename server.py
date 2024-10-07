import sys
import selectors
import socket
import threading
import types

HOST = '127.0.0.1' # localhost
PORT = 65432 # Port to listen on

sel = selectors.DefaultSelector()
#peers = []
socket_list = []
s = socket.socket()
s.bind(('127.0.0.1', 8001))
s.listen()

def socket_target(conn):
    while True:
        data = conn.recv(1024)
        if not data:
            break:
        conn.send(data)

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print(f"Accepted connection from {addr}")
    #peers.append(addr[0])
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            data.outb += recv_data
        else:
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print(f"Echoing {data.outb!r} to {data.addr}")
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]

# def sendPeers(peers, connections):
#     p = ""
#     for peer in peers:
#         p = p + peer+ ","
#     for connection in connections:
#         connection.send( b""+bytes(p, "utf-8"))

host, port = HOST, PORT
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print(f"Listening on {(host, port)}")
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)


while True:
    conn, address = s.accept()
    socket_list.append(conn)
    #threading.Thread(target= socket_target, args = (conns,)).start
try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)
                
            
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()
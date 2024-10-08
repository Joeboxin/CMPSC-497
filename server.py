import socket
import threading

socket_list = []
s = socket.socket()

HOST = "127.0.0.1"  # local host
PORT = 8001         # port to listen on
CHUNK_SIZE = 1024

s.bind((HOST,PORT))
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
    threading.Thread(target = socket_target, args = (conn, )).start

# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#     s.bind((HOST,PORT))
#     s.listen()
#     conn, addr = s.accept()
#     with conn:
#         print("connected by", addr)
#         while True:
#             data = conn.recv(1024)
#             if not data:
#                 break
#             conn.sendall(data)
#         s.close()

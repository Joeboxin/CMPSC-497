import socket

HOST = "127.0.0.1"  # server's hostname or ip address
PORT = 8001         # port used by the server
s = socket.socket()
s.connect((HOST, PORT))

while True:
    line = input('')
    if line == 'exit':
        break
    s.send(line.encode('unf-8'))

# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#     s.connect((HOST, PORT))
#     s.sendall(b'Hello, world')
#     data = s.recv(1024)
#     print('Received:', data.decode('utf-8')) # had to fix w this line since the print statement after close wouldn't work
#     s.close()

# print('Received', str(data), encoding='utf-8')

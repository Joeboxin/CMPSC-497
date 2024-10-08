import socket
import selectors
import types
import sys
import os

HOST = "127.0.0.1"
PORT = 65432
CHUNK_SIZE = 1024

sel = selectors.DefaultSelector()
messages = [b"Message 1 from client.", b"Message 2 from client."]


"""Opens the specified number of connections and registers them


"""
def start_connections(host, port, num_conns):
    server_addr = (host, port)
    for i in range(0, num_conns):
        connid = i + 1
        print(f"Starting connection {connid} to {server_addr}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(server_addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        data = types.SimpleNamespace(
            connid=connid,
            msg_total=sum(len(m) for m in messages),
            recv_total=0,
            messages=messages.copy(),
            outb=b"",
        )
        sel.register(sock, events, data=data)

"""Accepts a connections and turns off blocking to allow multiple connections


"""
def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

"""Gets socket and data with given key and mask, the masking shifts the data to receive the right number and order of bits

If there is any received data, it will set received data total to the sum of itself and received data
When it there is no received data or the received data is equal to the total data in the message, then it will close and unregister the socket

data.outb = buffer that holds the message
If the registered event is a write event, it will set the data out will pop from the the message stack (FIFO)
then checks if there is any data to write, if so then sends as much data as it can to the socket
The last line removes the part of the message that has already been sent
"""
def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            print(f"Received {recv_data!r} from connection {data.connid}")
            data.recv_total += len(recv_data)
        if not recv_data or data.recv_total == data.msg_total:
            print(f"Closing connection {data.connid}")
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        if data.outb:
            print(f"Sending {data.outb!r} to connection {data.connid}")
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]

def start_peer(server_ip):
    conn = 0
    start_connections(HOST, PORT, 1)  # Start a connection using the defined function

    while True:
        arg = input("Enter arg (REGISTER, LIST, DOWNLOAD): ").strip()

        if arg.startswith("REGISTER"):
            conn += 1
            _, filename = arg.split()
            total_chunks = os.path.getsize(filename) // CHUNK_SIZE + 1
            message = f"REGISTER_FILE {filename} {total_chunks}".encode('utf-8')

            # Iterate through the registered connections and append the message
            for key, _ in sel.get_map().items():
                if isinstance(key.data, types.SimpleNamespace):
                    key.data.messages.append(message)  # Ensure key.data is not an int
                    break  # Only send to one connection for now

        elif arg == "LIST":
            list_message = "REQUEST_FILE_LIST".encode('utf-8')
            for key, _ in sel.get_map().items():
                if isinstance(key.data, types.SimpleNamespace):
                    key.data.messages.append(list_message)
                    break  # Send to one connection

        elif arg.startswith("DOWNLOAD"):
            _, filename, total_chunks = arg.split()
            total_chunks = int(total_chunks)
            download_message = f"DOWNLOAD_FILE {filename} {total_chunks}".encode('utf-8')
            for key, _ in sel.get_map().items():
                if isinstance(key.data, types.SimpleNamespace):
                    key.data.messages.append(download_message)
                    break  # Send to one connection

if __name__ == "__main__":
    server_ip = input("Enter server IP: ")
    start_peer(server_ip)
    
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
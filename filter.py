import socket
import sys
import threading
import re
import libCheck

configRules = sys.argv[1]

def proxy_client_to_server(client_socket, server_socket):
    while True:
        # receive data from the client
        client_data = client_socket.recv(4096)

        if not client_data:
            break

        if libCheck.check_in(configRules, client_data):
            client_data=b''
        # forward client data to the local server
        else:
            server_socket.sendall(client_data)

    client_socket.close()

def proxy_server_to_client(client_socket, server_socket):
    while True:
        # receive data from the local server
        server_data = server_socket.recv(4096)

        if not server_data:
            break

        if libCheck.check_out(configRules, server_data):
            server_data=b''
        else:
    # forward local server data to the client
            client_socket.sendall(server_data)

    server_socket.close()

# set the external and local addresses and ports
external_address = '0.0.0.0'
external_port = int(sys.argv[2].split(':')[0])
local_address = '127.0.0.1'
local_port = int(sys.argv[2].split(':')[1])

# create a TCP/IP socket for the proxy server
proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind the proxy socket to the external address and port
proxy_socket.bind((external_address, external_port))

# listen for incoming connections
proxy_socket.listen(1)

print(f"Proxy server listening on {external_address}:{external_port}...")

while True:
    # accept incoming client connections
    client_socket, client_address = proxy_socket.accept()
    print(f"Accepted connection from {client_address}")

    # create a socket for the local server
    local_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect to the local server
    local_socket.connect((local_address, local_port))
    print(f"Connected to local server on {local_address}:{local_port}")

    # start forwarding traffic between the client and local server
    threading.Thread(target=proxy_client_to_server, args=(client_socket, local_socket)).start()
    threading.Thread(target=proxy_server_to_client, args=(client_socket, local_socket)).start()

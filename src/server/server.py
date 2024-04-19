import socket, ssl


from src.shared.protocol import HOST

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile="mycertfile", keyfile="mykeyfile")

bindsocket = socket.socket()
bindsocket.bind(HOST)
bindsocket.listen(5)

sock, addr = bindsocket.accept()
client = context.wrap_socket(sock, server_side=True)

req = client.recv(1024).decode()
if req == "Authenticate  ":
    client.sendall("Authenticated".encode())
else:
    client.sendall("Invalid Request".encode())

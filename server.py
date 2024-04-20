import socket, ssl


from src.shared.protocol import HOST
from src.shared.channel import Channel, ChannelType

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

bindsocket = socket.socket()
bindsocket.bind(HOST)
bindsocket.listen(5)


while True:
    sock, addr = bindsocket.accept()
    client = context.wrap_socket(sock, server_side=True)
    # Just a test
    data = client.recv(1024)
    if data:
        print(data.decode())
        chnl = Channel.deserialize(data.decode().split("\n")[1])
        print(chnl)
    client.close()

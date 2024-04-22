import socket, ssl
from sys import stdout
import threading
from loguru import logger
import loguru

from src.shared import loguru_config
from src.shared.protocol import HOST, RequestWrapper
from src.shared.channel import Channel, ChannelType
from src.shared import protocol, Request, RequestType, AbsDataClass, Serializeable
from src.server.client import Client


def main():
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")
    bindsocket = socket.socket()
    bindsocket.bind(HOST)
    bindsocket.listen(5)
    
    test = Channel(-1, "test", ChannelType.TEXT, 123)
    
    while True:
        sock, addr = bindsocket.accept()
        client_sock = context.wrap_socket(sock, server_side=True)
        client = Client(client_sock)
        threading.Thread(target=client.run, daemon=True).start()
        
        
if __name__ == "__main__":
    main()
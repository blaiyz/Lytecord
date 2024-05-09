import socket
import ssl
import threading
from sys import stdout

import loguru
from loguru import logger

from src.server.client import Client
from src.shared import (AbsDataClass, Request, RequestType, Serializeable,
                        loguru_config, protocol)
from src.shared.channel import Channel, ChannelType
from src.shared.protocol import HOST, RequestWrapper


def main():
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile="server.crt", keyfile="server.key")
    bindsocket = socket.socket()
    bindsocket.bind(HOST)
    bindsocket.listen(5)
    
    from src.server import db
    logger.info("Server started")
        
    while True:
        sock, addr = bindsocket.accept()
        client_sock = context.wrap_socket(sock, server_side=True)
        client = Client(client_sock)
        logger.info(f"Client connected: {addr}")
        # Creating and running an event loop in a separate thread
        t = threading.Thread(target=client.main_handler, daemon=True)
        t.name = f"Client handler thread; port: {client_sock.getpeername()[1]}"
        t.start()
        
        
if __name__ == "__main__":
    main()
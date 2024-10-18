import socket
import ssl
import sys
import threading
import signal
import time

from loguru import logger

from src.server.client import Client
# pylint: disable=unused-import
from src.shared import loguru_config
from src.shared.protocol import HOST


def signal_handler(_sig, _frame):
    logger.info("Shutting down server...")
    sys.exit(0)


def client_acceptor(bindsocket: socket.socket, context: ssl.SSLContext):
    while True:
        try:
            sock, addr = bindsocket.accept()
            logger.debug(f"Connection from {addr}")
            client_sock = context.wrap_socket(sock, server_side=True)
            client = Client(client_sock)
            logger.info(f"Client connected: {addr}")
            # Run client handler in a separate thread
            t = threading.Thread(target=client.main_handler, daemon=True)
            t.name = f"Client handler thread; port: {client_sock.getpeername()[1]}"
            t.start()
        except Exception as e:
            logger.exception(f"Error accepting client: {e}")


def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile="server.crt", keyfile="server.key")
    bindsocket = socket.socket()
    bindsocket.bind(("0.0.0.0", HOST[1]))
    bindsocket.listen(5)

    # Importing the db module starts the connection to the database
    # pylint: disable=unused-import
    from src.server import db
    logger.info("Server started")

    threading.Thread(target=client_acceptor, args=(bindsocket, context), daemon=True).start()

    # Main thread will just sleep, waiting for interrupt
    while True:
        time.sleep(9999)


if __name__ == "__main__":
    main()

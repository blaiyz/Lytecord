from re import S
import socket
import ssl
import threading
import asyncio
from loguru import logger

from src.shared import Request
from collections.abc import Callable


HOST = ("127.0.0.1", 24827)
NUMBER_OF_LENGTH_BYTES = 4

class SocketClosedException(Exception):
    pass

class RequestWrapper():
    def __init__(self, request: Request, id: int, callback: Callable[[Request], None] | None, subscribed: bool = False):
        self.request = request
        self.id = id
        self.callback = callback
        self.subscribed = subscribed

def send(wrapped: RequestWrapper, socket: ssl.SSLSocket):
    id = wrapped.id
    req = wrapped.request
    subbed = wrapped.subscribed

    data = f"{id}\n{subbed}\n{req.serialize()}"
    logger.info(f"Sending: {data}")
    encoded = data.encode()
    length = len(encoded).to_bytes(NUMBER_OF_LENGTH_BYTES, "big")
    socket.sendall(length + encoded)

def receive(socket: ssl.SSLSocket) -> tuple[Request, int, bool]:
    length = int.from_bytes(socket.recv(NUMBER_OF_LENGTH_BYTES), "big")
    if length == 0:
        raise SocketClosedException(f"Socket was closed: {socket}")
    data = socket.recv(length).decode()
    logger.info(f"Received: {data}")
    id, subbed, req = data.split("\n", maxsplit=2)
    subbed = subbed == "True"
    return Request.deserialize(req), int(id), subbed
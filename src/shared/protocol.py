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
MAX_DATA_LOG_LENGTH = 500

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
    encoded = data.encode()
    length = len(encoded).to_bytes(NUMBER_OF_LENGTH_BYTES, "big")
    logger.info(f"Sending {len(encoded)} bytes>>>>>>({socket.getpeername()})\n{data if len(data) < MAX_DATA_LOG_LENGTH else data[:MAX_DATA_LOG_LENGTH] + '...[TRUNCATED]'}")
    socket.sendall(length + encoded)

def receive(socket: ssl.SSLSocket) -> tuple[Request, int, bool]:
    length = int.from_bytes(socket.recv(NUMBER_OF_LENGTH_BYTES), "big")
    if length == 0:
        raise SocketClosedException(f"Socket was closed: {socket}")
    data = socket.recv(length).decode()
    logger.info(f"Received {length} bytes<<<<<<({socket.getpeername()})\n{data if len(data) < MAX_DATA_LOG_LENGTH else data[:MAX_DATA_LOG_LENGTH] + '...[TRUNCATED]'}")
    id, subbed, req = data.split("\n", maxsplit=2)
    subbed = subbed == "True"
    return Request.deserialize(req), int(id), subbed
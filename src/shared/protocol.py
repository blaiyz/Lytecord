import socket
from collections.abc import Callable

from loguru import logger

from src.shared import Request

HOST = ("10.30.56.221", 24827)
NUMBER_OF_LENGTH_BYTES = 4
MAX_DATA_LOG_LENGTH = 500
CERT = "server.crt"


class SocketClosedException(Exception):
    pass


class RequestWrapper():
    def __init__(self, request: Request, request_id: int, callback: Callable[[Request], None] | None, subscribed: bool = False):
        self.request = request
        self.id = request_id
        self.callback = callback
        self.subscribed = subscribed


def send(wrapped: RequestWrapper, socket: socket.socket):
    """
    Send a request to the given socket.
    
    The request is wrapped in a RequestWrapper object.
    """
    request_id = wrapped.id
    req = wrapped.request
    subbed = wrapped.subscribed

    data = f"{request_id}\n{subbed}\n{req.serialize()}"
    encoded = data.encode()
    length = len(encoded).to_bytes(NUMBER_OF_LENGTH_BYTES, "big")
    logger.info(
        f"Sending {len(encoded)} bytes>>>>>>({socket.getpeername()})\n{data if len(data) < MAX_DATA_LOG_LENGTH else data[:MAX_DATA_LOG_LENGTH] + '...[TRUNCATED]'}")
    socket.sendall(length + encoded)


def receive(socket: socket.socket) -> tuple[Request, int, bool]:
    """
    Receive a request from the given socket.
    
    Returns a tuple of the request, the request id, and whether the request is for a subscribed request.
    """
    length = int.from_bytes(_recvall(socket, NUMBER_OF_LENGTH_BYTES), "big")
    if length == 0:
        raise SocketClosedException(f"Socket was closed: {socket}")
    data = _recvall(socket, length).decode()
    logger.info(
        f"<<<<<<Received {length} bytes ({socket.getpeername()})\n{data if len(data) < MAX_DATA_LOG_LENGTH else data[:MAX_DATA_LOG_LENGTH] + '...[TRUNCATED]'}")
    id, subbed, req = data.split("\n", maxsplit=2)
    subbed = subbed == "True"
    return Request.deserialize(req), int(id), subbed


def _recvall(socket: socket.socket, length: int) -> bytes:
    """
    Receive `length` bytes from the given socket.
    
    Raises a SocketClosedException if the socket is closed.
    """
    batches: list[bytes] = []
    total = 0
    while total < length:
        batch = socket.recv(length - total)
        if not batch:
            raise SocketClosedException(f"Socket was closed: {socket}")
        total += len(batch)
        batches.append(batch)
    return b"".join(batches)

from __future__ import annotations

import threading
from queue import Queue
from ssl import SSLSocket

from loguru import logger

from src.shared import Request, RequestType, User
from src.shared import protocol
from src.shared.protocol import RequestWrapper


class Client():
    """
    Represents a client connection to the server.
    
    Attributes:
    - socket: The socket object representing the connection
    - name: The address/port of the client
    - user: The user object that the client is currently authenticated as
    - _response_queue: A queue of responses to send to the client
    - _condition: A condition variable to notify the main handler thread
    - _stop: A flag to stop the main handler thread
    - current_channel: The channel subscription that the client is currently subscribed to
    """

    def __init__(self, socket: SSLSocket):
        self._socket = socket
        self.name = socket.getpeername()
        self.user: User | None = None
        self._response_queue: Queue[RequestWrapper] = Queue()
        self._condition = threading.Condition()
        self._stop = False

        # Circular import fix
        from src.server import channel_manager
        self.current_channel: channel_manager.ChannelSubscription | None = None

    def _receiver_thread(self):
        while not self._stop:
            try:
                request, req_id, subbed = protocol.receive(self._socket)
            except protocol.SocketClosedException:
                self._stop = True
                with self._condition:
                    self._condition.notify()
                return

            # Circular import fix
            from src.server import request_handler

            try:
                response = request_handler.handle_request(request, req_id, subbed, self)
            # pylint: disable=broad-except
            except Exception as e:
                logger.exception(f"Caught unexpected exception in receiver thread: {e}")
                response = Request(RequestType.ERROR, {"message": "Internal server error"})

            wrapped = RequestWrapper(response, req_id, None, subbed)
            self._response_queue.put(wrapped)
            with self._condition:
                self._condition.notify()

    def add_response(self, wrapped: RequestWrapper):
        self._response_queue.put(wrapped)
        with self._condition:
            self._condition.notify()

    def main_handler(self):
        receiver_thread = threading.Thread(target=self._receiver_thread, daemon=True)
        receiver_thread.name = f"Client receiver thread; port: {self.name[1]}"

        try:
            receiver_thread.start()
            with self._condition:
                try:
                    while not self._stop:
                        self._condition.wait_for(lambda: not self._response_queue.empty() or self._stop)
                        if self._stop:
                            break

                        while not self._response_queue.empty():
                            response = self._response_queue.get()
                            protocol.send(response, self._socket)
                # pylint: disable=broad-except
                except Exception as _:
                    logger.error("Caught exception in main handler")
                    self._stop = True

        # pylint: disable=broad-except
        except Exception as _:
            logger.exception("Caught exception in main handler")
        finally:
            logger.info("Closing client")
            receiver_thread.join()
            if self.current_channel:
                self.current_channel.stop()
            try:
                self._socket.close()
            # pylint: disable=broad-except
            except Exception as _:
                pass
            logger.debug("Closed client")

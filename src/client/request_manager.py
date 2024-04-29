from customtkinter import CTk

from queue import Queue
import socket
import ssl
import threading
from threading import Thread
from collections.abc import Callable
import time
from loguru import logger


from src.shared.request import Request, RequestType
from src.shared import protocol
from src.shared.protocol import RequestWrapper, SocketClosedException


# The maximum number of requests that can be sent at once
# Should be enough (after all you don't send 1000 requests at once)
MAX_ID = 2**10


class RequestManager():
    def __init__(self, socket: ssl.SSLSocket, app: CTk):
        self._sock = socket
        self._app = app
        self._continue = False
        # outgoing
        self._requests: Queue[RequestWrapper] = Queue()
        self._current_id = 0
        self._sender = Thread(target=self._run_sender, daemon=True)
        self._sender_condition = threading.Condition()
        self._send_lock = threading.Lock()
        
        # incoming
        # normal means one time requests, while subscribed requests
        # persist until the client unsubscribes (useful for things like
        # getting new messages)
        self._normal_requests: dict[int, RequestWrapper] = {}
        self._normal_lock = threading.Lock()
        self._subscribed_requests: dict[int, RequestWrapper] = {}
        self._subscribed_lock = threading.Lock()
        self._receiver = Thread(target=self._run_receiver, daemon=True)


    def begin(self):
        if not self._continue:
            self._continue = True
            self._sender.start()
            self._receiver.start()
        
    def stop(self):
        if self._continue:
            self._continue = False
            with self._sender_condition:
                self._sender_condition.notify()
            self._sender.join()
            self._receiver.join()
        
    def _run_sender(self):
        with self._sender_condition:
            while self._continue:
                self._sender_condition.wait_for(lambda: not self._requests.empty() or not self._continue)
                if not self._continue:
                    break
                req = self._requests.get()
                id, subbed = req.id, req.subscribed
                if subbed:
                    with self._subscribed_lock:
                        self._subscribed_requests[id] = req
                else:
                    with self._normal_lock:
                        self._normal_requests[id] = req
                protocol.send(req, self._sock)
            
            
    def _run_receiver(self):
        while self._continue:
            try:
                req, id, subbed = protocol.receive(self._sock)
                error = req.request_type == RequestType.ERROR
                if error:
                    logger.warning(f"Received error from server: {req.data['message']}")

                if subbed:
                    with self._subscribed_lock:
                        wrapped = self._subscribed_requests.get(id, None)
                        if not wrapped:
                            continue
                        if error:
                            logger.warning(f"From subscribed request: {wrapped.request.request_type} {wrapped.request.data}")
                            continue
                        
                        if wrapped.callback:
                            self._app.after_idle(wrapped.callback, req)
                        
                else:
                    with self._normal_lock:
                        wrapped = self._normal_requests.pop(id, None)
                        if not wrapped:
                            continue
                        if error:
                            logger.warning(f"From regular request: {wrapped.request.request_type} {wrapped.request.data}")
                            continue
                            
                        if wrapped.callback:
                            self._app.after_idle(wrapped.callback, req)
            except SocketClosedException:
                logger.warning("Socket closed")
                break
            except Exception as e:
                logger.exception(f"Caught exception in receiver: {e}")
                break
            
    def request(self, req: Request, callback: Callable[[Request], None]):
        """
        Send a request to the server. The callback will be called when a response
        is received.
        """
        wrapped = RequestWrapper(req, self._current_id, callback)
        self._current_id = (self._current_id + 1) % MAX_ID
        with self._send_lock:
            with self._sender_condition:
                self._requests.put(wrapped)
                self._sender_condition.notify()
        
    def subscribe(self, req: Request, callback: Callable[[Request], None]) -> int:
        """
        Subscribe to a request. This means that the callback will be called
        each time a response is received for the provided request.
        Unlike normal requests, subscribed requests persist until the client
        unsubscribes.
        
        The returned number is the id of the request, which is used to unsubscribe.
        """
        wrapped = RequestWrapper(req, self._current_id, callback, True)
        self._current_id = (self._current_id + 1) % MAX_ID
        with self._send_lock:
            with self._sender_condition:
                self._requests.put(wrapped)
                self._sender_condition.notify()
        return wrapped.id
        
    def unsubscribe(self, id: int, request: Request):
        """
        Unsubscribe from a request, using the id returned from subscribe.
        Provide a request that will let the server know that you want to
        unsubscribe.
        """
        with self._send_lock:
            with self._subscribed_lock:
                self._subscribed_requests.pop(id, None)
        def callback(req: Request):
            pass
        self.request(request, callback)
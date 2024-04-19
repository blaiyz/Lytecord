from collections import deque
import socket
import ssl
import threading
from threading import Thread

from src.shared.request import Request, RequestType


class RequestManager():
    def __init__(self, socket: ssl.SSLSocket):
        self.sock = socket
        self._requests: list[Request] = []
        self._lock = threading.Lock()
        self._condition = threading.Condition(self._lock)
        self._sender = Thread(target=self._run_sender)
        self._continue = False
        
    def begin(self):
        if not self._continue:
            self._continue = True
            self._sender.start()
        
    def stop(self):
        if self._continue:
            self._continue = False
            self._sender.join()
        
    def _run_sender(self):
        while self._continue:
            with self._lock:
                while len(self._requests) == 0:
                    self._condition.wait()  # Wait until notified

                req = self._requests.pop(0)
                self.sock.sendall(req.serialize().encode())
                    
    def add_request(self, req: Request):
        with self._lock:
            self._requests.append(req)
            self._condition.notify() 
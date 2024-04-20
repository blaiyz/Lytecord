from queue import Queue
import socket
import ssl
import select
import threading
from threading import Thread

from src.shared.request import Request, RequestType


class RequestManager():
    def __init__(self, socket: ssl.SSLSocket):
        self.sock = socket
        self._requests: Queue[Request] = Queue()
        self._lock = threading.Lock()
        self._sender = Thread(target=self._run_sender, daemon=True)
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
            req = self._requests.get()
            self.sock.sendall(req.serialize().encode())
            # self.sock.recv(1024)
            
    def add_request(self, req: Request):
        self._requests.put(req)
from __future__ import annotations
from ssl import SSLSocket
import threading
import queue
from queue import Queue
from loguru import logger


from src.shared import *
from src.shared import protocol
from src.shared.protocol import RequestWrapper


class Client():
    def __init__(self, socket: SSLSocket):
        self._socket = socket
        self.user: User | None = None
        self._response_queue: Queue[RequestWrapper] = Queue()
        self._stop = False
    
        
    def _set_user(self, user: User):
        self.user = user
        
    def _receiver_thread(self, event: threading.Event):
        try:
            request, id, subbed = protocol.receive(self._socket)
        except protocol.SocketClosedException:
            self._stop = True
            event.set()
            return
        
        # Circular import fix
        from src.server import request_handler
        response = request_handler.handle_request(request, id, subbed, self)
        wrapped = RequestWrapper(response, id, None, subbed)
        self._response_queue.put(wrapped)
        event.set()
        
        
    def main_handler(self):
        event = threading.Event()
        t = threading.Thread(target=self._receiver_thread, args=(event,), daemon=True)

        try:
            t.start()
            while not self._stop and event.wait():
                try:
                    while not self._response_queue.empty():
                        response = self._response_queue.get()
                        protocol.send(response, self._socket)
                    event.clear()
                except Exception as e:
                    print(e)
                    logger.error("Caught exception in main handler")
                    self._stop = True
        except Exception as e:
            print(e)
            logger.error("Caught exception in main handler")
        finally:
            logger.info("Closing client")
            t.join()
            try:
                self._socket.close()
            except:
                pass
            logger.debug("Closed client")

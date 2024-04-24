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
        self._condition = threading.Condition()
        self._stop = False
    
        
    def _set_user(self, user: User):
        self.user = user
        
    def _receiver_thread(self):
        while not self._stop:
            try:
                request, id, subbed = protocol.receive(self._socket)
            except protocol.SocketClosedException:
                self._stop = True
                with self._condition:
                    self._condition.notify()
                return
            
            # Circular import fix
            from src.server import request_handler
            response = request_handler.handle_request(request, id, subbed, self)
            wrapped = RequestWrapper(response, id, None, subbed)
            self._response_queue.put(wrapped)
            self._condition.notify()
            
    def add_response(self, wrapped: RequestWrapper):
        self._response_queue.put(wrapped)
        with self._condition:
            self._condition.notify()
        
        
    def main_handler(self):
        t = threading.Thread(target=self._receiver_thread, daemon=True)

        try:
            t.start()
            with self._condition:
                try:
                    while not self._stop:
                        self._condition.wait_for(lambda: not self._response_queue.empty() or self._stop)
                        if self._stop:
                            break
        
                        while not self._response_queue.empty():
                            response = self._response_queue.get()
                            protocol.send(response, self._socket)
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

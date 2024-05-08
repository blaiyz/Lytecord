from __future__ import annotations

import queue
import threading
from queue import Queue
from ssl import SSLSocket

from loguru import logger

from src.shared import *
from src.shared import protocol
from src.shared.protocol import RequestWrapper


class Client():
    def __init__(self, socket: SSLSocket):
        self._socket = socket
        self.name = socket.getpeername()
        self.user: User | None = None
        self._response_queue: Queue[RequestWrapper] = Queue()
        self._condition = threading.Condition()
        self._stop = False
        self.current_user: User | None = None
        
        # Sorry :(
        from src.server import channel_manager
        self.current_channel: channel_manager.ChannelSubscription | None = None
    
        
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
            
            try:
                response = request_handler.handle_request(request, id, subbed, self)
            except Exception as e:
                logger.exception(f"Caught unexpected exception in receiver thread: {e}")
                response = Request(RequestType.ERROR, {"message": "Internal server error"})
                
            wrapped = RequestWrapper(response, id, None, subbed)
            self._response_queue.put(wrapped)
            with self._condition:
                self._condition.notify()
            
    def add_response(self, wrapped: RequestWrapper):
        self._response_queue.put(wrapped)
        with self._condition:
            self._condition.notify()
        
        
    def main_handler(self):
        t = threading.Thread(target=self._receiver_thread, daemon=True)
        t.name = f"Client receiver thread; port: {self.name[1]}"

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
            if self.current_channel:
                self.current_channel.stop()
            try:
                self._socket.close()
            except:
                pass
            logger.debug("Closed client")

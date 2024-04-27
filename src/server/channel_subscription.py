import threading
from loguru import logger

from src.server.client import Client
from src.shared.channel import Channel
from src.server import channel_manager
from src.shared.message import Message
from src.shared.protocol import RequestWrapper
from src.shared.request import Request, RequestType

class ChannelSubscription():
    def __init__(self, client: Client, id: int, channel: Channel):
        self.client = client
        # This is NOT the channel id, but the subscription id
        self._id = id
        self.channel = channel
        self.server_channel: channel_manager.ServerChannel | None = None
        self._last_message_id = 0
        self._stop = False
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.name = f"Channel subscription thread {client.name}"
        self._condition = threading.Condition()
        self._startup_event = threading.Event()

    def begin(self, last_message_id: int = 0):
        if not self._stop and not self._startup_event.is_set():
            self._last_message_id = last_message_id
            self._thread.start()
            self._startup_event.wait()
            self.server_channel = channel_manager.subscribe(self)

            
    def stop(self):
        with self._condition:
            self._stop = True
            logger.debug("got here")
            channel_manager.unsubscribe(self)
            logger.debug('unsubscribed')
            self.server_channel = None
            self._condition.notify()
            logger.debug('notified')
        self._thread.join()
        
    def _run(self):
        with self._condition:
            self._startup_event.set()
            logger.debug("event set")
            while not self._stop:
                self._condition.wait()
                logger.debug(f"woke up {self._id}, {self._stop}")
                if self._stop:
                    break
                
                if not self.server_channel:
                    continue
                
                messages = self.server_channel.get_messages(self._last_message_id)
                if len(messages) == 0:
                    continue
                
                for message in messages[::-1]:
                    self.client.add_response(self.create_response(message))
                self._last_message_id = messages[0].id if len(messages) > 0 else self._last_message_id
                    
    def create_response(self, message: Message) -> RequestWrapper:
        request = Request(RequestType.CHANNEL_SUBSCRIPTION, {"message": message})
        wrapped = RequestWrapper(request, self._id, None, True)
        return wrapped
        
                    
    def wake_up(self):
        with self._condition:
            self._condition.notify()
            
    def send_message(self, message: Message):
        if not self.server_channel:
            logger.warning("Tried to send message to None channel, please set channel first")
            return False
        
        self._last_message_id = message.id
        self.server_channel.broadcast(message, self)
        return True
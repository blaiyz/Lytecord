import bisect
from collections.abc import Callable
from datetime import datetime

from loguru import logger

from src.client.client import Client
from src.shared.channel import Channel
from src.shared.message import TAG_BYTE_LENGTH, Message

THRESHOLD = 30

class MessageManager():
    """
    This class is basically the message interface between channel_box and networking,
    which manages sending and receiving messages, and updating channel_box.
    It saves messages in a list and allows channel_box to take batches
    of messages from it, to improve performance.
    """
    def __init__(self, client: Client):
        # Client will be the networking class
        self._client = client
        self._channel: Channel | None = None
        self._messages: list[Message] = []
        self.new_message_callback: Callable | None = None
        # Flag of whether reached the top of the channel (loaded all possible messages)
        self._top: bool = False
        
    def set_channel(self, channel: Channel | None, received: Callable | None = None):
        logger.debug(f"Setting channel to {channel}")
        if channel == self._channel:
            return
        
        if self._channel is not None:
            self._client.unsubscribe_channel()
            logger.debug("unsubscribed")
            
        self._messages.clear()
        self._channel = channel
        self._top = False
        
        if channel is not None:
            def callback():
                self._client.subscribe_channel(channel, self.new_message)
                if received is not None:
                    received()
                
            self.fetch_messages(received=callback)
        
    
    def fetch_messages(self, from_id: int = 0, count: int = 100, received: Callable | None = None):
        """
        Fetch messages from the server.
        
        If from_id is 0, fetches messages from the top.
        Fetches all the messages sent before the id.
        
        Calls the option received callback when the messages are received.
        """
        if self._channel is None:
            logger.warning("Tried to fetch messages from None channel, please set channel first")
            return
        
        def callback(messages: list[Message]):
            if messages == []:
                self._top = True
            for message in messages:
                self.insert_sorted(message)
            if received is not None:
                received()
                
        logger.debug(f"Fetching messages from {from_id} with count {count}")
        self._client.get_messages(self._channel.id, from_id, count, callback=callback)
        
            
    def get_messages(self, id: int, before = True, count: int = THRESHOLD - 5) -> list[Message]:
        """
        Used by channel_box to load more messages.
        
        If before is True, returns messages before (not including) `id`, otherwise after (not including).
        If id is 0, returns the latest messages (`before` is ignored in this case).
        
        Internally, tries to fetch more messages if the user is getting close to the top.
        Another call may be needed to get the messages.
        """
        if self._channel is None:
            logger.warning("Tried to get messages from None channel, please set channel first")
            return []
        if count <= 0:
            logger.warning("Tried to get 0 or less messages")
            return []
        
        if id == 0:
            return self._messages[0:count]
        else:
            if not before:
                # If trying to get messages after the latest message
                if self._messages[0].id <= id:
                    return []
                
                # PLEASE DO NOT REMOVE THE MINUS
                # IT TOOK ME WAY TOO LONG TO DEBUG
                index = bisect.bisect_left(self._messages, -id, key=lambda x: x.sort_key())
                logger.debug(f"Index: {index}, i-c: {max(index - count, 0)}")
                return self._messages[max(index - count, 0):index]
            
            # If trying to get messages before the oldest message (that is currently fetched)
            if self._messages[-1].id >= id:
                return []
            else:
                #logger.debug(f"id: {id}, Messages\n" + "\n".join([str(m) for m in self._messages]))
                
                # PLEASE DO NOT REMOVE THE MINUS
                index = bisect.bisect_right(self._messages, -id, key=lambda x: x.sort_key())
                logger.debug(f"Index: {index}, i+c: {min(index + count, len(self._messages))}")
                ret = self._messages[index:min(index + count, len(self._messages))]
            
            # If the user is getting close or reached the top, fetch more messages
            if not self._top and (len(self._messages) - (index + count) < THRESHOLD or ret == []):
                self.fetch_messages(from_id=self._messages[-1].id)
            
            return ret
            
    def insert_sorted(self, message: Message):
        if self._messages is None:
            logger.warning("Tried to insert message into None message list, please set channel first")
            return
        
        if message not in self._messages:
            bisect.insort(self._messages, message, key=lambda x: x.sort_key())
            
    def send_message(self, message: Message):
        if self._channel is None:
            logger.warning("Cannot send message in a None channel, please set channel first")
            return
        
        
        self._client.send_message(message, callback=self.new_message)
    
    def new_message(self, message: Message | None):
        if message is None:
            logger.warning("Received None message")
            return
        if self._messages is None:
            logger.warning("Cannot send message in a None channel, please set channel first")
            return
        
        logger.info(f"New message: {message}")
        self.insert_sorted(message)
        if self.new_message_callback is not None:
            self.new_message_callback(message)
            
    
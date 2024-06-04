from __future__ import annotations
import bisect
import threading

from loguru import logger

from src.shared.channel import Channel
from src.shared.message import Message
from src.server import channel_subscription

BUFFER_SIZE = 30

class MessagePublisher:
    def __init__(self, channel: Channel):
        self.channel = channel
        self._lock = threading.Lock()
        self._subscriptions: list[channel_subscription.ChannelSubscription] = []
        self._buffer: list[Message] = []

    def add_subscription(self, sub: channel_subscription.ChannelSubscription):
        logger.debug(f"Adding subscription {sub} to channel {self.channel}")
        with self._lock:
            self._subscriptions.append(sub)

    def remove_subscription(self, sub: channel_subscription.ChannelSubscription):
        with self._lock:
            self._subscriptions.remove(sub)

    def is_empty(self):
        with self._lock:
            return len(self._subscriptions) == 0

    def broadcast(self, message: Message, sender: channel_subscription.ChannelSubscription):
        """
        Broadcast a message to all subscribers.
        """
        logger.debug(f"Broadcasting message {message} to channel {self.channel}")
        with self._lock:
            if message in self._buffer:
                return

            bisect.insort(self._buffer, message, key=lambda x: x.sort_key())
            if len(self._buffer) > BUFFER_SIZE:
                self._buffer.pop()
            for sub in self._subscriptions:
                if sub != sender:
                    logger.debug(f"waking up {sub}")
                    sub.wake_up()
        logger.success(f"Message {message} broadcasted to channel {self.channel}")

    def get_messages(self, after: int):
        """
        Return messages after the given id
        """
        with self._lock:
            if len(self._subscriptions) == 0:
                return []

            if len(self._buffer) == 0:
                return []

            if self._buffer[0].id < after:
                return []

            index = bisect.bisect_left(self._buffer, -after, key=lambda x: x.sort_key())
            return self._buffer[:index]
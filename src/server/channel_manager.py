import threading

from loguru import logger

from src.server.channel_subscription import ChannelSubscription
from src.server.message_publisher import MessagePublisher

lock = threading.Lock()
publishers: dict[int, MessagePublisher] = {}


def subscribe(client: ChannelSubscription, last_message_id: int = 0):
    channel_id = client.channel.id
    with lock:
        if channel_id not in publishers:
            publishers[channel_id] = MessagePublisher(client.channel)
        publishers[channel_id].add_subscription(client)

    client.begin(publishers[channel_id], last_message_id)
    return publishers[channel_id]


def unsubscribe(client: ChannelSubscription):
    channel_id = client.channel.id
    with lock:
        logger.debug("acquired lock")
        if channel_id in publishers:
            publishers[channel_id].remove_subscription(client)
            if publishers[channel_id].is_empty():
                del publishers[channel_id]
    client.stop()


def get_channel(channel_id: int):
    with lock:
        return publishers.get(channel_id, None)

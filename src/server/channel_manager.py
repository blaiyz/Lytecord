import threading

from loguru import logger

from src.server.channel_subscription import ChannelSubscription
from src.server.message_publisher import MessagePublisher

lock = threading.Lock()
publishers: dict[int, MessagePublisher] = {}

def subscribe(client_sub: ChannelSubscription, last_message_id: int = 0):
    """
    Subscribe a client to a channel.
    If the channel publisher does not exist, it will be created.
    """
    channel_id = client_sub.channel.id
    with lock:
        if channel_id not in publishers:
            publishers[channel_id] = MessagePublisher(client_sub.channel)
        publishers[channel_id].add_subscription(client_sub)

    client_sub.begin(publishers[channel_id], last_message_id)
    logger.success(f"Client {client_sub.client.name} subscribed to channel {client_sub.channel.name}")
    return publishers[channel_id]


def unsubscribe(client_sub: ChannelSubscription):
    """
    Unsubscribe a client from a channel.
    If the channel publisher is empty, it will be deleted.
    """
    channel_id = client_sub.channel.id
    with lock:
        if channel_id in publishers:
            publishers[channel_id].remove_subscription(client_sub)
            if publishers[channel_id].is_empty():
                del publishers[channel_id]
    client_sub.stop()
    logger.success(f"Client {client_sub.client.name} unsubscribed from channel {client_sub.channel.name}")
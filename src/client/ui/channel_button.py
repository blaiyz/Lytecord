import customtkinter as ctk
from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton, CTkFont, CTkScrollableFrame
from loguru import logger

from src.client.client import Client
from src.client.ui.channel_box import ChannelBox
from src.shared.channel import Channel
from src.client.ui.design import HASHTAG_ICON_DARK, HASHTAG_ICON_LIGHT


HEIGHT = 40

class ChannelButton(CTkButton):
    def __init__(self, *args, channel: Channel, channel_box: ChannelBox, client: Client, **kwargs):
        icon = ctk.CTkImage(light_image=HASHTAG_ICON_LIGHT, dark_image=HASHTAG_ICON_DARK, size=(20, 20))
        super().__init__(*args, border_width=3, text=channel.name, command=self.on_click, font=("", 17), corner_radius=5, height=HEIGHT, anchor="w", border_color="#52a9ff", image=icon, border_spacing=5, **kwargs)

        self._client = client
        self._channel = channel
        self._cb = channel_box

    @property 
    def channel(self):
        return self._channel
    
    def on_click(self):
        logger.debug(f"ChannelButton {self._channel} clicked")
        if self._cb.set_channel(self._channel):
            return
        else:
            logger.warning("Failed to set channel")
        
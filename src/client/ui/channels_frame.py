import customtkinter as ctk
from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton, CTkFont, CTkScrollableFrame
import tkinter as tk
from PIL import Image
from loguru import logger

from src.client.ui.channel_button import ChannelButton
from src.client.ui.channel_box import ChannelBox
from src.shared.channel import Channel



class ChannelsFrame(CTkScrollableFrame):
    def __init__(self, *args, channel_box: ChannelBox, **kwargs):
        super().__init__(*args, corner_radius=0, fg_color="transparent", **kwargs)

        self._cb = channel_box
        self.grid_columnconfigure(0, weight=1)

        self._channels: list[ChannelButton] = []

    def add_channel(self, c: Channel):
        logger.debug(f"Adding channel {c}")
        channel_button = ChannelButton(self, channel_box=self._cb, channel=c)
        channel_button.grid(row=len(self._channels), column=0, sticky="ew", padx=5, pady=5)
        self._channels.append(channel_button)

    def clear_channels(self):
        logger.debug(f"Clearing channels")
        
        self._cb.set_channel(None)
        for channel in self._channels:
            channel.destroy()
        self._channels.clear()
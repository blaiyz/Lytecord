import customtkinter as ctk
from customtkinter import (CTkButton, CTkEntry, CTkFont, CTkFrame, CTkImage,
                           CTkLabel, CTkScrollableFrame)
from loguru import logger
from PIL import Image

from src.client.client import Client
from src.client.ui.channels_frame import ChannelsFrame
from src.client.ui.design import GUILD_ICON_DARK, GUILD_ICON_LIGHT
from src.shared.channel import Channel, ChannelType
from src.shared.guild import Guild

SIZE = 60

COLOR = "#2c2c2c"
HOVER_COLOR = "#727272"


class GuildButton(CTkButton):
    def __init__(self, *args, guild: Guild, cf: ChannelsFrame, client: Client, **kwargs):
        if guild is None:
            raise TypeError("guild cannot be None")
        if cf is None:
            raise TypeError("cf cannot be None")

        icon = CTkImage(light_image=GUILD_ICON_LIGHT, dark_image=GUILD_ICON_DARK, size=(SIZE, SIZE))
        super().__init__(*args, text="", corner_radius=15, width=SIZE + 10, height=SIZE + 10, border_spacing=0,
                         command=self.on_click, image=icon, fg_color=COLOR, hover_color=HOVER_COLOR, **kwargs)
        self.client = client
        self._guild = guild
        self._channels_frame = cf
        self._fetching = False

        # TODO: implement icon, implement font resize for when no icon is present

    def on_click(self):
        logger.debug(f"GuildButton {self._guild} clicked")
        if self._channels_frame.load(new_guild=self._guild):
            return
        else:
            logger.warning("Failed to load channels")

    @property
    def guild(self):
        return self._guild

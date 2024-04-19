import customtkinter as ctk
from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton, CTkFont, CTkScrollableFrame, CTkImage
from PIL import Image
from loguru import logger

from src.shared.guild import Guild
from src.shared.channel import Channel, ChannelType
from src.client.ui.channels_frame import ChannelsFrame
from src.client.ui.design import GUILD_ICON_LIGHT, GUILD_ICON_DARK

SIZE = 60

COLOR = "#2c2c2c"
HOVER_COLOR = "#727272"


class GuildButton(CTkButton):
    def __init__(self, *args, guild: Guild, cf: ChannelsFrame, **kwargs):
        if guild is None:
            raise TypeError("guild cannot be None")
        if cf is None:
            raise TypeError("cf cannot be None")


        icon = CTkImage(light_image=GUILD_ICON_LIGHT, dark_image=GUILD_ICON_DARK, size=(SIZE, SIZE))
        super().__init__(*args, text="", corner_radius=15, width=SIZE+10, height=SIZE+10, border_spacing=0, command=self.on_click, image=icon, fg_color=COLOR, hover_color=HOVER_COLOR, **kwargs)
        self._guild = guild
        self._cf = cf
        self._channel_list = [Channel(i, f"channel{i}@guild{self._guild.id}", ChannelType.TEXT, self._guild.id) for i in range(1, 11)]


        # TODO: implement icon, implement font resize for when no icon is present

    def on_click(self):
        logger.debug(f"GuildButton {self._guild} clicked")
        self._cf.clear_channels()
        for channel in self._channel_list:
            self._cf.add_channel(channel)

    @property 
    def guild(self):
        return self._guild
    
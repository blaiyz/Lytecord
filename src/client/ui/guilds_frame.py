import customtkinter as ctk
from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton, CTkFont, CTkScrollableFrame
from PIL import Image
from loguru import logger


from src.client.ui.channels_frame import ChannelsFrame
from src.client.ui.guild_button import GuildButton, SIZE
from src.shared.guild import Guild


WIDTH = 100
BG_COLOR = "#1c1c2d"


class GuildsFrame(CTkScrollableFrame):
    def __init__(self, *args, cf: ChannelsFrame, **kwargs):
        super().__init__(*args, corner_radius=0, width=WIDTH, fg_color=BG_COLOR, scrollbar_fg_color="transparent", **kwargs)
        

        self.guilds: list[GuildButton] = []
        self._cf = cf

        self.grid_columnconfigure(0, weight=1)

        for i in range(1, 11):
            self.add_guild(i)

    def add_guild(self, id: int):
        guild_button = GuildButton(self, guild=Guild(id, "test"), cf = self._cf)
        guild_button.grid(row=len(self.guilds), column=0, padx=5, pady=5)
        self.guilds.insert(id, guild_button)

    def remove_guild(self, id: int):
        self.guilds[id].destroy()
        self.guilds.pop(id)
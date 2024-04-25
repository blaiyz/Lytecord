import customtkinter as ctk
from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton, CTkFont, CTkScrollableFrame
from PIL import Image
from loguru import logger


from src.client.client import Client
from src.client.ui.channels_frame import ChannelsFrame
from src.client.ui.guild_button import GuildButton, SIZE
from src.shared.guild import Guild


WIDTH = 100
BG_COLOR = "#1c1c2d"


class GuildsFrame(CTkScrollableFrame):
    def __init__(self, *args, cf: ChannelsFrame, client: Client, **kwargs):
        super().__init__(*args, corner_radius=0, width=WIDTH, fg_color=BG_COLOR, scrollbar_fg_color="transparent", **kwargs)
        

        self.client = client
        self.guilds: list[GuildButton] = []
        self._cf = cf

        self.grid_columnconfigure(0, weight=1)

    def add_guild(self, guild: Guild):
        if [g for g in self.guilds if g.guild.id == guild.id]:
            return
        
        guild_button = GuildButton(self, guild=guild, cf = self._cf, client=self.client)
        guild_button.grid(row=len(self.guilds), column=0, padx=5, pady=5)
        self.guilds.append(guild_button)

    def remove_guild(self, guild: Guild):
        self.guilds[guild.id].destroy()
        self.guilds = [g for g in self.guilds if g.guild.id != guild.id]
        
        # Re-grid
        gb: GuildButton
        for i, gb in enumerate(self.guilds):
            gb.grid(row=i, column=0, padx=5, pady=5)
        
    def clear_guilds(self):
        for guild in self.guilds:
            guild.destroy()
        self.guilds.clear()
        
    def load(self):
        def callback(guilds: list[Guild]):
            for guild in guilds:
                self.add_guild(guild)
        
        self.client.get_guilds(callback=callback)
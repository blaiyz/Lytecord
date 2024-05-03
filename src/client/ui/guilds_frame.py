from turtle import window_height
import customtkinter as ctk
from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton, CTkFont, CTkScrollableFrame, CTkImage, CTkInputDialog
from CTkMessagebox import CTkMessagebox
from ctkcomponents import CTkBanner


from PIL import Image
from loguru import logger


from src.client.client import Client
from src.client.ui.channels_frame import ChannelsFrame
from src.client.ui.guild_button import GuildButton, SIZE
from src.client.ui.design import JOIN_GUILD_ICON_DARK, JOIN_GUILD_ICON_LIGHT, CREATE_GUILD_ICON_DARK, CREATE_GUILD_ICON_LIGHT
from src.shared.guild import Guild, MAX_NAME_LENGTH, MIN_NAME_LENGTH


WIDTH = 100
BG_COLOR = "#1c1c2d"
BUTTON_SIZE = 50

class GuildsFrame(CTkFrame):
    def __init__(self, *args, channels_frame: ChannelsFrame, client: Client, **kwargs):
        super().__init__(*args, corner_radius=0, width=WIDTH, fg_color=BG_COLOR, **kwargs)
        

        self.client = client
        self.guilds: list[GuildButton] = []
        self._channels_frame = channels_frame
        self._loading = False

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._scroll_frame = CTkScrollableFrame(self, width=WIDTH, fg_color="transparent", scrollbar_fg_color="transparent")
        self._scroll_frame.grid_columnconfigure(0, weight=1)
        self._scroll_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        
        
        join_icon = CTkImage(light_image=JOIN_GUILD_ICON_LIGHT, dark_image=JOIN_GUILD_ICON_DARK, size=(BUTTON_SIZE, BUTTON_SIZE))
        self._join_guild_button = CTkButton(self, text='', corner_radius=20, fg_color="transparent", hover_color="#858585", image=join_icon, command=self.on_join_guild, width=BUTTON_SIZE, height=BUTTON_SIZE)
        self._join_guild_button.grid(row=2, column=0, padx=10, pady=5)
        
        create_icon = CTkImage(light_image=CREATE_GUILD_ICON_LIGHT, dark_image=CREATE_GUILD_ICON_DARK, size=(BUTTON_SIZE, BUTTON_SIZE))
        self._create_guild_button = CTkButton(self, text='', corner_radius=20, fg_color="transparent", hover_color="#858585", image=create_icon, command=self.on_create_guild, width=BUTTON_SIZE, height=BUTTON_SIZE)
        self._create_guild_button.grid(row=3, column=0, padx=10, pady=(5, 15))

    def add_guild(self, guild: Guild):
        if [g for g in self.guilds if g.guild.id == guild.id]:
            return
        
        guild_button = GuildButton(self._scroll_frame, guild=guild, cf = self._channels_frame, client=self.client)
        guild_button.grid(row=len(self.guilds), column=0, padx=5, pady=5)
        self.guilds.append(guild_button)

    def remove_guild(self, guild: Guild):
        self.guilds[guild.id].destroy()
        self.guilds = [g for g in self.guilds if g.guild.id != guild.id]
        
        # Re-grid
        gb: GuildButton
        for i, gb in enumerate(self.guilds):
            gb.grid(row=i, column=0, padx=5, pady=5)
        
    def clear_guilds(self) -> bool:
        logger.debug("Clearing guilds")
        if self._loading:
            logger.warning("Currently loading guilds")
            return False
        
        for guild in self.guilds:
            guild.destroy()
        self.guilds.clear()
        return True
    
    def center_top_level(self, top_level: ctk.CTkToplevel):
        root = self.winfo_toplevel()
        x = int(root.winfo_width() * .5 + self.winfo_rootx() - .5 * top_level.winfo_width())
        y = int(root.winfo_height() * .5 + self.winfo_rooty() - .5 * top_level.winfo_height())
        top_level.geometry(f"+{x}+{y}")    
    
    def on_join_guild(self):
        dialog = CTkInputDialog(title="Join Guild", text="Enter the invite code of the guild")
        self.center_top_level(dialog)
        
        code = dialog.get_input()
        logger.debug(f"Joining guild with code {code}")
        
        if code is None:
            return
        
        if len(code) > 16:
            box = CTkMessagebox(title="Join Guild", message="Invalid code", icon="cancel", option_1="Ok")
            self.center_top_level(box)
            return
        
        def callback(guild: Guild | None, message: str):
            if guild is not None:
                self.add_guild(guild)
                box = CTkMessagebox(title="Join Guild", message=f"Successfully joined guild with name \"{guild.name}\"", icon="check", option_1="Ok")
                self.center_top_level(box)
                return
            
            box = CTkMessagebox(title="Join Guild", message="Could not join the guild: " + message, icon="cancel", option_1="Ok", option_2="Retry")
            self.center_top_level(box)
            
            response = box.get()
            if response == "Retry":
                self.after_idle(self.on_join_guild)
                
        self.client.join_guild(code, callback=callback)
        
    def on_create_guild(self):       
        dialog = CTkInputDialog(title="Create Guild", text="Enter the name of the new guild")
        self.center_top_level(dialog)

        name = dialog.get_input()
        logger.debug(f"Creating guild with name {name}")
        
        if name is None:
            return

        message = None
        if len(name) > MAX_NAME_LENGTH:
            message = f"Name cannot be more than {MAX_NAME_LENGTH} characters long"
        elif len(name) < MIN_NAME_LENGTH:
            message = f"Name cannot be less than {MIN_NAME_LENGTH} characters long"
        else:
            try:
                guild = Guild(0, name, 0)
            except:
                message = "Invalid name"
        
        if message:
            box = CTkMessagebox(title="Create Guild", message=message, icon="cancel", option_1="Ok", option_2="Retry")
            self.center_top_level(box)
            
            response = box.get()
            if response == "Retry":
                self.after_idle(self.on_create_guild)
            return
        
        
        def callback(guild: Guild | None, message: str):
            if guild is not None:
                self.add_guild(guild)
                box = CTkMessagebox(title="Create Guild", message=f"Successfully created guild with name \"{guild.name}\"", icon="check", option_1="Ok")
                self.center_top_level(box)
                return
            
            box = CTkMessagebox(title="Create Guild", message="Error at creating guild: " + message, icon="cancel", option_1="Ok", option_2="Retry")
            self.center_top_level(box)
            
            response = box.get()
            if response == "Retry":
                self.after_idle(self.on_create_guild)
        
        self.client.create_guild(guild.name, callback=callback)

    def load(self):
        if self._loading:
            logger.warning("Already loading guilds")
            return
        
        def callback(guilds: list[Guild]):
            for guild in guilds:
                self.add_guild(guild)
            self._loading = False
        
        self.client.get_guilds(callback=callback)
        self._loading = True
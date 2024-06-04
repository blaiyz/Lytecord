import os
from enum import Enum
from sys import stderr
from tkinter import Tk
from typing import Callable, Tuple

import customtkinter
from loguru import logger
from PIL import Image

import src.shared.loguru_config
from src.client.client import AuthType, Client
from src.client.ui.login_frame import LoginFrame
from src.client.ui.main_frame import MainFrame
from src.shared import login_utils
from src.shared.protocol import HOST

customtkinter.set_appearance_mode("dark")

# Get system scaling
# scaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
# customtkinter.set_window_scaling(scaleFactor)
# customtkinter.set_widget_scaling(scaleFactor)


MIN_WIDTH = 0
MIN_HEIGHT = 0
START_WIDTH = 1000
START_HEIGHT = 600


class App(customtkinter.CTk):
    width = START_WIDTH
    height = START_HEIGHT

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.client = Client(*HOST, self)

        self.title("Lytcord")
        scale_factor = self._get_window_scaling()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int(((screen_width/2) - (self.width/2)) * scale_factor)
        y = int(((screen_height/2) - (self.height/1.5)) * scale_factor) + 100
        self.geometry(f"{self.width}x{self.height}+{int(x)}+{int(y)}")

        self.grid_rowconfigure(0, weight=1, minsize=0)
        self.grid_columnconfigure(0, weight=1, minsize=0)
        
        self.login_frame = LoginFrame(self, auth = self.authenticate)
        self.login_frame.grid(row=0, column=0, sticky='nsew')

        self.main_frame = MainFrame(self, client= self.client)
        self.main_frame.grid(row=0, column=0, sticky='nsew')
        self.main_frame.grid_remove()

        self.current_frame = self.login_frame
        self.app_state = AppState.IDLE

        self.bind("<Button-1>", self.click_event, add="+")

    def authenticate(self, subtype: AuthType, username: str, password: str, color: str, callback: Callable[[bool, str], None]):
        if self.app_state == AppState.LOGGING_IN:
            callback(False, "Already Logging in")

        logger.info(f"Authenticating user: {username} with password: {password} in mode: {subtype}")
        
        def c(success: bool, message: str):
            if success:
                self.app_state = AppState.LOGGED
                self.after(0, self.switch_frame)
                callback(True, message)
            callback(False, message)
            
        if not login_utils.is_valid_username(username):
            if subtype == AuthType.REGISTER:
                callback(False, "Invalid username")
            else:
                callback(False, "Invalid credentials")
            return
        if not login_utils.is_valid_password(password):
            if subtype == AuthType.REGISTER:
                callback(False, "Invalid/weak password")
            else:
                callback(False, "Invalid credentials")
            return
        if subtype == AuthType.REGISTER and not login_utils.is_valid_color(color):
            callback(False, "Bad name color, try a different one")
            return
            
        self.client.authenticate(subtype, username, password, color, c)

    
    def switch_frame(self):
        if self.current_frame == self.login_frame:
            self.login_frame.grid_remove()
            self.main_frame.grid()
            self.main_frame.load()
            self.state("zoomed")
            self.current_frame = self.main_frame
        else:
            self.main_frame.grid_remove()
            self.login_frame.grid()
            self.state("normal")
            self.current_frame = self.login_frame

    def click_event(self, event):
        """
        Created this function just to unfocus entries
        after clicking outside
        """
        x,y = self.winfo_pointerxy()            
        widget = self.winfo_containing(x,y)     

        if widget == None:
            return
        widget.focus_set()
        
    def close_client(self):
        self.client.close()


class AppState(Enum):
    IDLE = 1
    LOGGING_IN = 2
    LOGGED = 3


if __name__ == "__main__":
    app = App()
    app.mainloop()
    app.close_client()
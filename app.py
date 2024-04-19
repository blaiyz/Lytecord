import customtkinter
from loguru import logger
from PIL import Image
from enum import Enum
from typing import Tuple
import os


from src.client.ui.login_frame import LoginFrame
from src.client.ui.main_frame import MainFrame

customtkinter.set_appearance_mode("system")

# Get system scaling
# scaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
# customtkinter.set_window_scaling(scaleFactor)
# customtkinter.set_widget_scaling(scaleFactor)


MIN_WIDTH = 0
MIN_HEIGHT = 0
START_WIDTH = 600
START_HEIGHT = 600



class App(customtkinter.CTk):
    width = START_WIDTH
    height = START_HEIGHT

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


        scale_factor = self._get_window_scaling()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int(((screen_width/2) - (self.width/2)) * scale_factor)
        y = int(((screen_height/2) - (self.height/1.5)) * scale_factor)
        self.title("Lytcord")
        self.geometry(f"{self.width}x{self.height}+{int(x)}+{int(y)}")

        self.grid_rowconfigure(0, weight=1, minsize=0)
        self.grid_columnconfigure(0, weight=1, minsize=0)
        
        self.login_frame = LoginFrame(self, auth = self.authenticate)
        self.login_frame.grid(row=0, column=0, sticky='nsew')

        self.main_frame = MainFrame(self)
        self.main_frame.grid(row=0, column=0, sticky='nsew')
        self.main_frame.grid_remove()

        self.current_frame = self.login_frame
        self.app_state = AppState.IDLE

        self.bind("<Button-1>", self.click_event, add="+")

    def authenticate(self, mode: str, username: str, password: str) -> Tuple[bool, str | None]:
        if self.app_state == AppState.LOGGIN_IN:
            return False, "Already Logging in"

        logger.info(f"Authenticating user: {username} with password: {password} in mode: {mode}")

        # Implement authentication logic here, for now accept empty queries
        if username == "":
            # After authenticating, client should start fetching
            # data from server, for now just artificial wait
            # After that switch to main frame
            # Will probably use threading for this (or asyncio)
            self.after(500, self.switch_frame)
            self.app_state = AppState.LOGGIN_IN
        
            return True, None

        return False, "Authentication not implemented"
    
    def switch_frame(self):
        if self.current_frame == self.login_frame:
            self.login_frame.grid_remove()
            self.main_frame.grid()
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



class AppState(Enum):
    IDLE = 1
    LOGGIN_IN = 2


if __name__ == "__main__":
    app = App()
    app.mainloop()

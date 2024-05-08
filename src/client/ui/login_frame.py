import os
import tkinter as tk
from collections.abc import Callable

import customtkinter as ctk
from customtkinter import CTkButton, CTkEntry, CTkFont, CTkFrame, CTkLabel

from src.client.client import AuthType

LOWER_ROW_GRID = 100
AUTH_BUTTON_ROW = 50
FG_COLOR = "#4028a1"



class LoginFrame(ctk.CTkFrame):
    def __init__(self, *args, auth: Callable, **kwargs):
        super().__init__(*args, fg_color = FG_COLOR, corner_radius = 0, **kwargs)
        self.state = AuthType.LOGIN
        self.auth: Callable[[AuthType, str, str, Callable[[bool, str], None]], None] = auth
        
        self.grid_columnconfigure((0, 2), weight=2, minsize=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)


        # Add if there's time left
        # # load and create background image
        # current_path = os.path.dirname(os.path.realpath(__file__))
        # self.bg_image = ctk.CTkImage(im.open(current_path.replace("src\\client", "assets") + "\\login_screen_bg.jpg"))
        # self.canvas_widget = tk.Canvas(self) 
        # self.bg_image_label = ctk.CTkLabel(self, image=self.bg_image)
        # self.bg_image_label.grid(row=0, rowspan=3, column=0)


        # create login frame
        self.login_frame = CTkFrame(self, corner_radius=0, width=400)
        self.login_frame.grid(row=0, column=1, sticky="nsew", padx=100)
        self.login_frame.grid_columnconfigure((0, 2), weight=1)
        self.login_frame.grid_columnconfigure(1, )
        self.login_frame.grid_rowconfigure(AUTH_BUTTON_ROW + 2, weight=5)
        self.login_frame.grid_rowconfigure(0, weight=1)

        self.lytecord_label = ctk.CTkLabel(self.login_frame, text="Lytecord", font=ctk.CTkFont(size=60, weight="bold"), anchor="center")
        self.lytecord_label.grid(row=1, column = 1, padx=40, pady=(20, 0), sticky="ew")
        self.auth_label = ctk.CTkLabel(self.login_frame, text="Welcome Back!\nPlease login to continue.",
                    font=ctk.CTkFont(size=20, weight="bold"), anchor="center")
        self.auth_label.grid(row=2, column=1, padx=20, pady=(40, 15), sticky="ew")

        # create entry fields
        self.username_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Username")
        self.username_entry.grid(row=3, column=1, pady=10, sticky="ew", padx=20)

        self.password_entry = ctk.CTkEntry(self.login_frame, show="*", placeholder_text="Password")
        self.password_entry.grid(row=4, column=1, pady=10, sticky="ew", padx=20)

        self.password_confirm = ctk.CTkEntry(self.login_frame, show="*", placeholder_text="Confirm Password")
        self.password_confirm.grid(row=AUTH_BUTTON_ROW - 1, column=1, pady=10, sticky="ew", padx=20)
        self.password_confirm.grid_remove()

        # create login button
        self.auth_button = ctk.CTkButton(self.login_frame, text="Login", command=self.auth_button_event)
        self.auth_button.grid(row=AUTH_BUTTON_ROW, column=1, pady=10)

        # create error label
        self.error_label = ctk.CTkLabel(self.login_frame, text="Error logging in!", text_color="red")
        self.error_label.grid(row=AUTH_BUTTON_ROW + 1, column=1, pady=10)
        self.error_label.grid_remove()

        # create switch auth mode label
        self.switch_auth_mode_label = ctk.CTkLabel(self.login_frame, text="Don't have an account?", font=ctk.CTkFont(size=18, weight="bold"), anchor="center")
        self.switch_auth_mode_label.grid(row = LOWER_ROW_GRID, column = 1, padx=40, pady=(40, 0), sticky="sew")

        # create signup button
        self.switch_auth_mode_button = ctk.CTkButton(self.login_frame, text="Signup", command=self.switch_authentication_mode)
        self.switch_auth_mode_button.grid(row=LOWER_ROW_GRID + 1, column=1, pady=(10, 30))
        
        self.bind("<Return>", self.auth_button_event, add=True)
        self.username_entry.bind("<Return>", self.auth_button_event, add=True)
        self.password_entry.bind("<Return>", self.auth_button_event, add=True)
        self.password_confirm.bind("<Return>", self.auth_button_event, add=True)



    def auth_button_event(self, *args):
        
        # Implement login logic here
        # If login is successful, hide login frame and show main frame
        # If login is unsuccessful, show error message
        def callback(success: bool, message: str):
            if not success:
                self.error_label.configure(text=message, text_color="red")
            else:
                self.error_label.configure(text= "Success!\n Loggin in...", text_color="green")
            self.error_label.grid()
            
        if self.state == AuthType.REGISTER:
            if self.password_entry.get() != self.password_confirm.get():
                callback(False, "Passwords do not match")
                return
            
        self.error_label.configure(text="Authenticating...", text_color=("black", "white"))
        self.error_label.grid()
        self.auth(self.state, self.username_entry.get(), self.password_entry.get(), callback)

        

    def switch_authentication_mode(self):
        if self.state == AuthType.LOGIN:
            self.auth_label.configure(text="Create an account\nPlease sign up to continue.")
            self.switch_auth_mode_label.configure(text = "Already have an account?")
            self.password_confirm.grid()
        else:
            self.auth_label.configure(text="Welcome Back!\nPlease login to continue.")
            self.switch_auth_mode_label.configure(text = "Don't have an account?")
            self.password_confirm.grid_remove()
        
        self.state = self.state.opp()
        self.auth_button.configure(text=self.state.value)
        self.switch_auth_mode_button.configure(text=self.state.opp().value)
        self.error_label.grid_remove()
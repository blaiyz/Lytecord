import customtkinter as ctk
from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton, CTkFont, CTkTextbox, CTkProgressBar, CTkImage
import tkinter as tk
from datetime import datetime
from loguru import logger
from PIL import Image, ImageDraw
from PIL.Image import Image as ImageType

from src.client.client import Client
from src.client.ui.design import IMG_ERR_ICON_LIGHT, IMG_ERR_ICON_DARK, IMG_ICON_LIGHT, IMG_ICON_DARK
from src.shared.attachment import Attachment

class LoadableImage(CTkFrame):
    def __init__(self, *args, image: ImageType | Attachment, corner_radius: int, client: Client, **kwargs):
        super().__init__(*args, corner_radius=corner_radius, **kwargs)
        self.client = client
        self._loading = False
        self._image = image
        self._corner_radius = corner_radius
        if isinstance(image, Attachment):
            
            self.width = image.width
            self.height = image.height
        else:
            self.width, self.height = image.size
        
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self._loading_animation = CTkProgressBar(self, mode="indeterminate")
        self._loading_animation.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        self._loading_animation.grid_remove()
        
        self._image_label = CTkLabel(self, text="", fg_color="transparent", corner_radius=0)
        self._image_label.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self._image_label.grid_remove()
    
    def _display_image(self):
        if isinstance(self._image, Attachment):
            logger.warning("Load image first")
            return
        
        converted = self.add_corners(self._image, self._corner_radius)
        image = CTkImage(light_image=converted, dark_image=converted, size=(self.width, self.height))
        
        self._image_label.configure(image=image)
        self._image_label.grid()
        
    
    def load(self):
        if self._loading:
            return
        self._loading = True
        
        if isinstance(self._image, ImageType):
            self._display_image()
            self._loading = False
            return
        
        def callback(image: ImageType | None, message: str):
            self._loading_animation.stop()
            self._loading_animation.grid_remove()
            if image is None:
                logger.error(f"Failed to load image: {message}")
                error_image = CTkImage(light_image=IMG_ERR_ICON_LIGHT, dark_image=IMG_ERR_ICON_DARK, size=(self.width-20, self.height-20))
                self._image_label.configure(image=error_image)
                self._image_label.grid()
                return
                
            self._image = image
            self._display_image()
                
        self._loading_animation.start()
        self._loading_animation.grid()
        
        self.client.get_
        
    def destroy(self):
        self._loading = True
        return super().destroy()
    
    @staticmethod
    def add_corners(image: ImageType, radius: int):
        """
        Adds rounded corners to an image
        """
        # Source: https://github.com/rudymohammadbali/ctk_components/blob/main/ctk_components.py Line 410
        
        circle = Image.new('L', (radius * 2, radius * 2), 0)
        draw = ImageDraw.Draw(circle)
        draw.ellipse((0, 0, radius * 2 - 1, radius * 2 - 1), fill=255)
        alpha = Image.new('L', image.size, 255)
        w, h = image.size
        alpha.paste(circle.crop((0, 0, radius, radius)), (0, 0))
        alpha.paste(circle.crop((0, radius, radius, radius * 2)), (0, h - radius))
        alpha.paste(circle.crop((radius, 0, radius * 2, radius)), (w - radius, 0))
        alpha.paste(circle.crop((radius, radius, radius * 2, radius * 2)), (w - radius, h - radius))
        image.putalpha(alpha)
        return image
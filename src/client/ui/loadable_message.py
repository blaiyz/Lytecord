from io import BytesIO
import time
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

MAX_DIMENSIONS = 2**9

class LoadableImage(CTkFrame):
    def __init__(self, *args, image: ImageType | Attachment, corner_radius: int, client: Client, **kwargs):
        if isinstance(image, Attachment):
            width = image.width
            height = image.height
        else:
            width, height = image.size
            
        if width > MAX_DIMENSIONS or height > MAX_DIMENSIONS:
            ratio = width / height
            if width > height:
                width = MAX_DIMENSIONS
                height = int(MAX_DIMENSIONS / ratio)
            else:
                height = MAX_DIMENSIONS
                width = int(MAX_DIMENSIONS * ratio)
        
        logger.debug(f"Image size: {width}x{height}")
        super().__init__(*args, corner_radius=corner_radius, width=width, height=height, **kwargs)
        self.client = client
        self._loading = False
        self._image = image
        self._corner_radius = corner_radius
        
        self.width, self.height = width, height
        
        self.grid_columnconfigure((0, 2), weight=1, minsize=10)
        self.grid_columnconfigure(1, minsize=width)
        self.grid_rowconfigure((0, 2), weight=1, minsize=10)
        self.grid_rowconfigure(1, minsize=height)
        
        self._loading_animation = CTkProgressBar(self, mode="indeterminate")
        self._loading_animation.grid(row=1, column=0, columnspan=3, sticky="ew", padx=20, pady=10)
        self._loading_animation.grid_remove()
        
        self._image_label = CTkLabel(self, text="", fg_color="transparent", corner_radius=0)
        self._image_label.grid(row=1, column=1, sticky="nsew", padx=0, pady=0)
        self._image_label.grid_remove()
    
    def _display_image(self):
        if isinstance(self._image, Attachment):
            logger.warning("Load image first")
            return
        
        logger.debug(f"size: {self._image.size}, format: {self._image.format}, mode: {self._image.mode}")
        
        converted = self.add_corners(self._image, self._corner_radius)
        logger.debug(f"width: {self.width}, height: {self.height}")
        image = CTkImage(light_image=self._image, size=(self.width, self.height))
        self.configure(corner_radius=0, fg_color="transparent")
        
        self._image_label.configure(image=image)
        self._image_label.grid()
        
        logger.info("Image loaded")
        
    def _failed_to_load(self, message: str):
        logger.error(message)
        error_image = CTkImage(light_image=IMG_ERR_ICON_LIGHT, dark_image=IMG_ERR_ICON_DARK, size=(150, 150))
        self._image_label.configure(image=error_image)
        self._image_label.grid()
    
    def load(self):
        if self._loading:
            return
        self._loading = True
        
        if isinstance(self._image, ImageType):
            self._display_image()
            self._loading = False
            return
        
        def callback(image_file: bytes | None, message: str):
            self._loading = False
            if not self.winfo_exists():
                return
            self._loading_animation.stop()
            self._loading_animation.grid_remove()
            
            if image_file is None:
                self._failed_to_load(f'Failed to load image: {message}')
                return
            
            try:
                image = Image.open(BytesIO(image_file))
            except Exception as e:
                logger.exception("Failed to open image")
                self._failed_to_load("Failed to open image")
                return
                
            self._image = image
            self._display_image()
                
        self._loading_animation.start()
        self._loading_animation.grid()
        
        self.client.get_attachment_file(self._image.id, callback)

    
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
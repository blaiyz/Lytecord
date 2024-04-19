import customtkinter as ctk
from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton, CTkFont, CTkTextbox
import tkinter as tk
from datetime import datetime
from loguru import logger
from PIL import Image, ImageDraw
from PIL.Image import Image as ImageType

from src.client.ui.design import IMG_ERR_ICON_LIGHT, IMG_ERR_ICON_DARK, IMG_ICON_LIGHT, IMG_ICON_DARK
from src.shared.attachment import Attachment

class LoadableMessage(CTkFrame):
    def __init__(self, *args, image: ImageType | Attachment | int, corner_radius: int, client, **kwargs):
        super().__init__(*args, corner_radius=corner_radius, **kwargs)
        
        
    
    
    
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
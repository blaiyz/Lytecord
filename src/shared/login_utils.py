import re

import bcrypt

from src.shared.user import User

USERNAME_REGEX = re.compile(r'^(?=.{3,20}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$')
PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d_@$!%*#?&]{8,50}$')

INVALID_COLORS = ['#2b2b2b']
THRESHOLD = 20


def is_valid_username(username: str) -> bool:
    return bool(USERNAME_REGEX.match(username))


def is_valid_password(password: str) -> bool:
    return bool(PASSWORD_REGEX.match(password))


def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def is_valid_color(color: str) -> bool:
    if len(color) != 7 or color[0] != "#":
        return False
    try:
        hex = color[1:]
        int(hex, 16)
    except ValueError:
        return False

    # Check color similarity to invalid colors
    for invalid_color in INVALID_COLORS:
        if User.color_distance(color, invalid_color) < THRESHOLD:
            return False
    return True

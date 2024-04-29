import re
import bcrypt

from src.server import db

USERNAME_REGEX = re.compile(r'^(?=.{3,20}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$')
PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d_@$!%*#?&]{8,50}$')


def is_valid_username(username: str) -> bool:
    return bool(USERNAME_REGEX.match(username))


def is_valid_password(password: str) -> bool:
    return bool(PASSWORD_REGEX.match(password))

def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
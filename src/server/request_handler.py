import functools
from loguru import logger

from src.shared import *
from src.server.client import Client

def handle_request(req: Request, id: int, subbed: bool, client: Client) -> Request:
    req_type = req.request_type
    
    match req_type:
        case RequestType.AUTHENTICATION:
            res_data = authenticate(req.data)
        case _:
            res_data = {"status": "error", "message": "Invalid request type"}
            
    return Request(req_type, res_data)
            

def authenticate(data: dict) -> dict:
    username: str = data["username"]
    password: str = data["password"]
    
    # Temporary
    if username == "" and password == "":
        return {"status": "success", "message": "Authenticated"}
    return {"status": "error", "message": "Invalid credentials"}

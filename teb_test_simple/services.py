import os
import hashlib
import hmac
import uuid
import urllib.parse
from typing import Dict

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def validate_hash(data: Dict[str, str], bot_token: str) -> bool:
    data = data.copy()
    true_hash = data.pop('hash')
    
    data_check_str = '\n'.join(
        f'{key}={value}' for key, value 
        in sorted(data.items())
        )

    data_check_str = urllib.parse.unquote(data_check_str).encode()

    secret_key = hashlib.sha256(bot_token.encode()).digest()
    hash = hmac.new(secret_key, data_check_str, digestmod=hashlib.sha256).hexdigest()
    return hmac.compare_digest(hash.encode(), true_hash.encode())

def check_parameters(auth_data: dict) -> dict:
    return {'id', 'hash'}.issubset(set(auth_data)) and auth_data

def generate_session_id() -> str:
    return str(uuid.uuid4())

def validate_age(message: types.Message) -> bool:
    try:
        age = int(message.text)
    except ValueError:
        return False
    return 13 < age < 101

def validate_sex(message: types.Message) -> bool:
    return message.text in ['Male', 'Female', 'Other']

def validate_username(message: types.Message) -> bool:
    return 1 < len(message.text) < 30

def validate_name(message: types.Message) -> bool:
    return 1 < len(message.text) < 30
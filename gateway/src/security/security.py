import random
import string
from typing import Dict, Optional


async def generate_token(length: int = 100) -> str:
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for _ in range(length))


async def find_first_key_by_value(data: Dict[str, str], search_value: str) -> Optional[str]:
    for key, value in data.items():
        if value == search_value:
            return key
    return None

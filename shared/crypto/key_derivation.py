from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes

SALT_SIZE = 16
KEY_LEN = 32
PBKDF2_ITERATIONS = 200_000


def generate_salt() -> bytes:
    return get_random_bytes(SALT_SIZE)


def derive_key(password: str, salt: bytes) -> bytes:
    if not password:
        raise ValueError("Password must not be empty.")
    return PBKDF2(password=password, salt=salt, dkLen=KEY_LEN, count=PBKDF2_ITERATIONS)
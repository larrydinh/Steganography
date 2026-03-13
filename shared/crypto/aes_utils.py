from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

NONCE_SIZE = 12


def encrypt_message(plaintext: bytes, key: bytes) -> tuple[bytes, bytes, bytes]:
    nonce = get_random_bytes(NONCE_SIZE)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    return nonce, ciphertext, tag


def decrypt_message(nonce: bytes, ciphertext: bytes, tag: bytes, key: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)
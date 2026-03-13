from shared.crypto.key_derivation import generate_salt, derive_key
from shared.crypto.aes_utils import encrypt_message, decrypt_message
from shared.crypto.payload_format import pack_encrypted_payload, unpack_encrypted_payload


def build_secure_payload(secret_text: str, password: str) -> bytes:
    plaintext = secret_text.encode("utf-8")
    salt = generate_salt()
    key = derive_key(password, salt)
    nonce, ciphertext, tag = encrypt_message(plaintext, key)
    return pack_encrypted_payload(salt, nonce, tag, ciphertext)


def recover_secure_payload(payload: bytes, password: str) -> str:
    salt, nonce, tag, ciphertext = unpack_encrypted_payload(payload)
    key = derive_key(password, salt)
    plaintext = decrypt_message(nonce, ciphertext, tag, key)
    return plaintext.decode("utf-8")
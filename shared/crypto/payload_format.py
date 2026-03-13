from shared.utils.bit_utils import int_to_fixed_bytes, fixed_bytes_to_int


def pack_encrypted_payload(salt: bytes, nonce: bytes, tag: bytes, ciphertext: bytes) -> bytes:
    payload = bytearray()
    payload += len(salt).to_bytes(1, "big")
    payload += salt
    payload += len(nonce).to_bytes(1, "big")
    payload += nonce
    payload += len(tag).to_bytes(1, "big")
    payload += tag
    payload += int_to_fixed_bytes(len(ciphertext), 4)
    payload += ciphertext
    return bytes(payload)


def unpack_encrypted_payload(data: bytes) -> tuple[bytes, bytes, bytes, bytes]:
    idx = 0

    salt_len = data[idx]
    idx += 1
    salt = data[idx:idx + salt_len]
    idx += salt_len

    nonce_len = data[idx]
    idx += 1
    nonce = data[idx:idx + nonce_len]
    idx += nonce_len

    tag_len = data[idx]
    idx += 1
    tag = data[idx:idx + tag_len]
    idx += tag_len

    ciphertext_len = fixed_bytes_to_int(data[idx:idx + 4])
    idx += 4
    ciphertext = data[idx:idx + ciphertext_len]

    return salt, nonce, tag, ciphertext
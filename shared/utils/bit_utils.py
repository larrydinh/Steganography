from typing import List


def bytes_to_bits(data: bytes) -> List[int]:
    bits: List[int] = []
    for byte in data:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    return bits


def bits_to_bytes(bits: List[int]) -> bytes:
    if len(bits) % 8 != 0:
        raise ValueError("Bit length must be a multiple of 8.")
    out = bytearray()
    for i in range(0, len(bits), 8):
        byte = 0
        for bit in bits[i:i + 8]:
            byte = (byte << 1) | bit
        out.append(byte)
    return bytes(out)


def int_to_fixed_bytes(value: int, length: int = 4) -> bytes:
    return value.to_bytes(length, byteorder="big")


def fixed_bytes_to_int(data: bytes) -> int:
    return int.from_bytes(data, byteorder="big")
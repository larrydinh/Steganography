import numpy as np

from shared.stego.dwt import embed_dwt, extract_dwt


def test_dwt_roundtrip():
    image = np.full((256, 256, 3), 128, dtype=np.uint8)
    payload = b"hello dwt"

    stego = embed_dwt(image, payload)
    recovered = extract_dwt(stego)

    assert recovered == payload
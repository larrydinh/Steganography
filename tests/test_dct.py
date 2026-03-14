import numpy as np

from shared.stego.dct import embed_dct, extract_dct


def test_dct_roundtrip():
    image = np.full((256, 256, 3), 128, dtype=np.uint8)
    payload = b"hello dct"

    stego = embed_dct(image, payload)
    recovered = extract_dct(stego)

    assert recovered == payload
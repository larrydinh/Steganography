from io import BytesIO
from PIL import Image
import numpy as np


def load_image_from_bytes(image_bytes: bytes) -> np.ndarray:
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    return np.array(image)


def save_image_to_png_bytes(image: np.ndarray) -> bytes:
    pil_image = Image.fromarray(image.astype("uint8"))
    buffer = BytesIO()
    pil_image.save(buffer, format="PNG")
    return buffer.getvalue()
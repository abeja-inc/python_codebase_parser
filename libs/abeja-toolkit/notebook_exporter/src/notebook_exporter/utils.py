import base64
import io
import random
import string
from io import BytesIO

from PIL import Image


def pil2bytes(image: Image.Image) -> BytesIO:
    """
    Convert PIL Image to BytesIO

    Parameters
    ----------
    image : PIL.Image.Image
        PIL Image object

    Returns
    -------
    BytesIO
        BytesIO object
    """
    num_byteio = io.BytesIO()
    image.save(num_byteio, format=image.format.lower() if image.format else "jpeg")
    num_byteio.seek(0)
    return num_byteio


def decode_image(image_encoded: str, as_utf8: bool = False) -> Image.Image:
    """
    Decode base64 encoded image

    Parameters
    ----------
    image_encoded : str
        base64 encoded image
    as_utf8 : bool
        If True, encode image_encoded as utf-8 before decoding base64

    Returns
    -------
    PIL.Image.Image
        PIL Image object
    """
    if not as_utf8:
        image_bytes = base64.b64decode(image_encoded)
    else:
        image_encoded_utf: bytes = image_encoded.encode("utf-8")
        image_bytes = base64.b64decode(image_encoded_utf)

    byteio = io.BytesIO(image_bytes)
    return Image.open(byteio)


def random_string(length: int = 20) -> str:
    """
    Generate random string

    Parameters
    ----------
    length : int
        Length of the random string

    Returns
    -------
    str
        Random string
    """
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))

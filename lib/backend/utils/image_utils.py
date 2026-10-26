import base64
import io
from PIL import Image

def base64_to_image(base64_str):
    """Convert base64 string to PIL Image"""
    image_bytes = base64.b64decode(base64_str)
    return Image.open(io.BytesIO(image_bytes))

def image_to_base64(image, format="JPEG", quality=80):
    """Convert PIL Image to compressed base64 string (JPEG default for minimal memory & network overhead)"""
    buffer = io.BytesIO()
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    image.save(buffer, format=format, quality=quality)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

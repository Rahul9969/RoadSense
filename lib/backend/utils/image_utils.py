import base64
import io
from PIL import Image

def base64_to_image(base64_str):
    """Convert base64 string to PIL Image"""
    image_bytes = base64.b64decode(base64_str)
    return Image.open(io.BytesIO(image_bytes))

def image_to_base64(image, format="PNG"):
    """Convert PIL Image to base64 string"""
    buffer = io.BytesIO()
    image.save(buffer, format=format)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

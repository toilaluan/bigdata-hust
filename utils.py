import base64
import requests
from PIL import Image
from io import BytesIO


def load_and_convert_image(url):
    try:
        img = load_image(url)
        img_base64 = image_to_base64(img)
        return img_base64  # Convert bytes to string
    except Exception as e:
        print(f"Error processing image: {e}")
        return None


def load_image(image_url):
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    return img


def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str

import base64
import requests
from PIL import Image
from io import BytesIO
import json
import numpy as np
import base64
from PIL import Image
import io
import matplotlib.pyplot as plt

# Function to decode and display an image
def display_image(encoded_image, title, price):
    # Decode the image
    price = price.replace("$","")
    image_data = base64.b64decode(encoded_image)
    image = Image.open(io.BytesIO(image_data))
    image.save(f"weaviate/tmp/{title}-{price}.png")
    # # Display the image
    plt.imshow(image)
    plt.title(f"{title} - ${price}")
    plt.axis('off')
    plt.show()

# Function to process and visualize the JSON file
def visualize_json(file_path):
    # Read the JSON file
    with open(file_path, 'r') as file:
        data = json.load(file)['data']['Get']['Estate']

    # Iterate over each item and display the image
    for item in data:
        # print(item)
        display_image(item['image'], item['title'], item['price'])



def load_and_convert_image(url):
    try:
        img = load_image(url)
        img_base64 = image_to_base64(img)
        return img_base64  # Convert bytes to string
    except Exception as e:
        print(f"Error processing image: {e}")
        return None



def load_image(image_url):
    try:
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        return img
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None


def image_to_base64(image):
    buffered = BytesIO()
    if isinstance(image, np.ndarray):
        image = Image.fromarray(image)
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str

def base64_to_image(img_str):
    img_data = base64.b64decode(img_str)
    img = Image.open(io.BytesIO(img_data))
    return img
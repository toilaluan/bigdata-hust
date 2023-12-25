import weaviate
from utils import load_image, image_to_base64, base64_to_image
import json
from PIL import Image
from io import BytesIO
from typing import Union

def query_an_image(image: Union[str, Image.Image]):
    """
    Query an image to Weaviate.
    """
    print("Querying an image...")
    if isinstance(image, str):
        image = load_image(image)
        
    image_base64 = image_to_base64(image)

    client = weaviate.Client("http://localhost:8080")
    # print all object
    nearImage = {"image": image_base64, "certainty": 0.6}
    try:
        results = (
            client.query.get("Estate", ["image", "title", "price", "estate_id", "description"]).with_limit(10).with_near_image(nearImage, encode=False).do()
        )
        results = results['data']['Get']['Estate']
    except KeyError:
        print("No result found")
        return [], []
    print(len(results))
    images = [base64_to_image(result['image']) for result in results]
    metadatas = [(result['title'], result['price'], result["estate_id"]) for result in results]

    return images, metadatas
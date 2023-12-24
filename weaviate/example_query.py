import weaviate
from utils import load_image, image_to_base64, visualize_json
import json

image_url = "https://hanoirealestate.com.vn/images/products/lake-view-2-bedroom-apartment-for-rent-in-quang-khanh-spacious-balcony_20231121163401.jpg"
image = load_image(image_url)
image.save("weaviate/tmp/query_image.png")
image_base64 = image_to_base64(image)

client = weaviate.Client("http://localhost:8080")

# print all object
result = client.query.get("Estate", properties=["title"]).do()

nearImage = {"image": image_base64, "certainty": 0.5}

result = (
    client.query.get("Estate", ["image", "title", "price"]).with_near_image(nearImage, encode=False).do()
)

with open("tmp/result.json", "w") as f:
    json.dump(result, f, indent=2)

visualize_json("tmp/result.json")
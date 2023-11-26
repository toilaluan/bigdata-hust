import weaviate
from utils import load_image, image_to_base64

image_url = "https://hanoirealestate.com.vn/images/products/lake-view-2-bedroom-apartment-for-rent-in-quang-khanh-spacious-balcony_20231121163401.jpg"
image = load_image(image_url)
image_base64 = image_to_base64(image)

client = weaviate.Client("http://localhost:8080")

# print all object
result = client.query.get("Estate", properties=["title"]).do()

nearImage = {"image": image_base64, "certainty": 0.05}

result = (
    client.query.get("Estate", "image").with_near_image(nearImage, encode=False).do()
)

print(result)

from kafka import KafkaConsumer
import json
from utils import load_and_convert_image, load_image
from minio import Minio
from io import BytesIO
import yaml
from tqdm import tqdm
import sys



BUCKET_NAME = "real-estate-images"

def main():
    minio_client = Minio(
        "127.0.0.1:9000",
        access_key="bigdata2023",
        secret_key="bigdata2023",
        secure=False
    )
    found = minio_client.bucket_exists(BUCKET_NAME)
    if not found:
        minio_client.make_bucket(BUCKET_NAME)
    else:
        print(f"Bucket {BUCKET_NAME} already exists")

    consumer = KafkaConsumer(
        'real-estate',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='my-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    while True:
        records = consumer.poll(1000) # timeout in millis , here set to 1 min

        record_list = []
        for tp, consumer_records in records.items():
            for consumer_record in consumer_records:
                message = consumer_record.value
                print(message['id'])
                temp_image_urls = message['image_urls'][:3]
                image_urls = []
                for i in range(len(image_urls)):
                    try:
                        minio_client.stat_object(BUCKET_NAME, f"{message['id']}/{i}.png")
                        print(f"Image {i} already exists")
                        continue
                    except:
                        image_urls.append(temp_image_urls[i])
                pil_images = [load_image(url) for url in message['image_urls'][:3]]
                pil_images = [image for image in pil_images if image is not None]
                id = message['id']
                for i, image in tqdm(enumerate(pil_images), total=len(pil_images)):
                    file_key = f"{i}.png"
                    temp_save_file = f"/tmp/{file_key}"
                    image.save(temp_save_file)
                    minio_client.fput_object(
                        BUCKET_NAME,
                        f"{id}/{i}.png",
                        temp_save_file,
                    )
        
        

if __name__ == '__main__':
    main()
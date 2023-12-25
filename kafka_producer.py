from kafka import KafkaProducer
import json
import time

with open("crawl_data/estate_data.json", "r", encoding="utf-8") as f:
    data_list = json.load(f)
# sort by id
data_list = sorted(data_list, key=lambda x: x["id"])
# Create a Kafka producer
producer = KafkaProducer(
    bootstrap_servers=["localhost:9092"],  # Kafka server address
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),  # Serializer for JSON
)

# Kafka topic name
topic_name = "real-estate"

# Send each dictionary as a separate message
for item in data_list:
    producer.send(topic_name, item)
    producer.flush()
    time.sleep(1)
    print(f"Sent an item. {item['id']}")

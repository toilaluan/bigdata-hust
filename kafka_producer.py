from kafka import KafkaProducer
import json

with open("crawl_data/estate_data.json", "r", encoding="utf-8") as f:
    data_list = json.load(f)

# Create a Kafka producer
producer = KafkaProducer(
    bootstrap_servers=["localhost:9092"],  # Kafka server address
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),  # Serializer for JSON
)

# Kafka topic name
topic_name = "your_topic"

# Send each dictionary as a separate message
for item in data_list:
    producer.send(topic_name, item)
    producer.flush()

print("Messages sent to Kafka")

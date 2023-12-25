from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StringType, ArrayType, StructField
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType
from utils import *
import weaviate


def weaviate_writer(df, epoch_id):
    # df = df.withColumn("uuid", col("id"))
    # rename id to estate_id
    df = df.withColumnRenamed("id", "estate_id")
    df.write.format("io.weaviate.spark.Weaviate") \
    .option("batchSize", 1) \
    .option("scheme", "http") \
    .option("host", "localhost:8080") \
    .option("className", "Estate") \
    .mode("append").save()


# Register UDF
load_and_convert_image_udf = udf(load_and_convert_image, StringType())

# Initialize Weaviate client
client = weaviate.Client("http://localhost:8080")
client.schema.delete_all()
client.schema.create_class(
    {
        "class": "Estate",
        "vectorizer": "multi2vec-clip",
        "moduleConfig": {
            "multi2vec-clip": {
                "textFields": ["title", "price", "description", "estate_id"],
                "imageFields": ["image"],
            }
        },
        "properties": [
            {"name": "title", "dataType": ["text"]},
            {"name": "price", "dataType": ["text"]},
            {"name": "description", "dataType": ["text"]},
            {"name": "image", "dataType": ["blob"]},
            {"name": "image_urls", "dataType": ["text[]"]},
            {"name": "estate_id", "dataType": ["text"]},
        ],
    }
)

# Initialize Spark Session
spark = (
    SparkSession.builder
    .config(
        "spark.jars",
        "https://github.com/weaviate/spark-connector/releases/download/v1.3.0/spark-connector-assembly-1.3.0.jar",  # specify the spark connector JAR
    )
    .config("spark.streaming.stopGracefullyOnShutdown", True)
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0")
    .config("spark.sql.shuffle.partitions", 4)
    .master("local[*]")
    .appName("weaviate")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("WARN")

# Define your schema corresponding to the dictionary keys
schema = (
    StructType()
    .add("title", StringType())
    .add("price", StringType())
    .add("image_urls", ArrayType(StringType()))
    .add("description", StringType())
    .add("id", StringType())
)
# Read from Kafka
df = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", "localhost:9092")
    .option("subscribe", "real-estate")
    .load()
)


# Deserialize JSON
df = df.select(from_json(col("value").cast("string"), schema).alias("data")).select(
    "data.*"
)

# Load base64 image
df = df.withColumn("first_image_url", col("image_urls").getItem(0))
df = df.withColumn("image", load_and_convert_image_udf(col("first_image_url")))
df = df.drop("first_image_url")
# Processing (just printing in this example)
query = (
    df.writeStream
    .foreachBatch(weaviate_writer)
    # .outputMode("append")
    # .format("console")
    .start()
)

query.awaitTermination()

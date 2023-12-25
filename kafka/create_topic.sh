sudo docker exec -it kafka /bin/sh -c \
"cd /opt/kafka_2.13-2.8.1/bin && kafka-topics.sh --zookeeper zookeeper:2181 --delete --topic real-estate"

sudo docker exec -it kafka /bin/sh -c \
"cd /opt/kafka_2.13-2.8.1/bin && kafka-topics.sh --create --zookeeper zookeeper:2181 --replication-factor 1 --partitions 1 --topic real-estate"
sudo docker exec -it kafka /bin/sh -c \
"cd /opt/kafka_2.13-2.8.1/bin && kafka-topics.sh --list --zookeeper zookeeper:2181"


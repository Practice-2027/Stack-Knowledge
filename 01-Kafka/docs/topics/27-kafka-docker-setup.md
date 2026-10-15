# 27. Kafka Docker Setup

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

docker-compose.yml runs cp-zookeeper:7.5.0 on 2181 and cp-kafka:7.5.0 on 9092. It advertises localhost:9092 for host scripts and kafka:29092 internally, enables auto topic creation, and uses one broker. Volumes are not declared, so persistence is not explicitly configured.

## Workflow

```text
docker compose up -d -> ZooKeeper -> broker -> Python clients.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

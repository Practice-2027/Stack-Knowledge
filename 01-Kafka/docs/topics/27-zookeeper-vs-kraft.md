# 27. ZooKeeper vs KRaft

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

This project uses ZooKeeper through KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181. It does not use KRaft. KRaft is Kafka's newer metadata mode; migration would require a different Compose configuration and is outside the current implementation.

## Workflow

```text
ZooKeeper coordinates broker metadata; broker serves records.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

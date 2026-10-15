# 8. Producer Message Flow

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

producer.send() passes a Python dictionary to the JSON serializer. Kafka receives bytes, assigns a partition and offset, and future.get() returns metadata. The code logs topic, partition, and offset after flush and acknowledgement.

## Workflow

```text
Dictionary -> JSON UTF-8 bytes -> broker -> partition/offset -> producer metadata.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

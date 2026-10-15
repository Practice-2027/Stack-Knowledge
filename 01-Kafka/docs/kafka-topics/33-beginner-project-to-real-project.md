# 33. Beginner Project to Real Project

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

The beginner stage is Flask -> one Kafka topic -> one worker. An intermediate system adds APIs, multiple consumer groups, and a database. Production adds multiple brokers, replication, observability, schema governance, security, and separate topics for business events.

## Workflow

```text
Scale by separating request handling, transport, workers, and storage.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

# 22. Request/Response vs Kafka

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

REST is synchronous request/response: the caller waits for a response. Kafka is asynchronous: the producer publishes an event and the consumer processes it later. This project uses REST for submission and status queries, Kafka for background task transport.

## Workflow

```text
POST submits intent; GET /tasks reads local status; Kafka carries work.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

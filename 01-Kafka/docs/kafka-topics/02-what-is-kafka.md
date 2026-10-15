# 2. What Is Kafka?

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

Kafka is a durable, distributed log. It lets the web request finish quickly while another process handles slow work later. In this project Kafka separates the Flask web server from the worker.

## Workflow

```text
Without Kafka: browser waits for work. With Kafka: browser submits an event, Kafka stores it, and the worker reads it when ready.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

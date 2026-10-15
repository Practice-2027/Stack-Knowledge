# 58. Final Project Report

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

Project: Apache Kafka Task Queue System. Language: Python. Library: Flask, kafka-python, Jinja2, colorama. Broker: localhost:9092, one Docker broker. Topic: task-queue. Group: task-processor-group. Producer: producer.py. Consumer: consumer.py. State: JSON files. API: four Flask routes. Missing: database, replication, security, schema registry, metrics, dead-letter topic, and true exactly-once processing.

## Workflow

```text
Recommended improvements: durable storage, multiple brokers, explicit partitions, secure listeners, monitoring, retries, idempotency, tests, and CI.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

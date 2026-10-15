# 1. Project Overview

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

This is an asynchronous task queue. A browser calls Flask, Flask creates a task record and publishes JSON to Kafka, and consumer.py processes it in the background. The dashboard reads local JSON state to show QUEUED, PROCESSING, or COMPLETED.

## Workflow

```text
User -> POST /submit-task -> producer.py -> task-queue -> consumer.py -> task_results.json -> GET /tasks -> dashboard
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

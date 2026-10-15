# 42. Complete API Flow

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

Implemented API routes are GET /, POST /submit-task, GET /tasks, and GET /health on port 5001. POST accepts JSON or form data. It creates the event and returns 201; the consumer does not respond synchronously to the original POST.

## Workflow

```text
Client -> Flask -> Kafka -> worker -> files -> GET /tasks.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

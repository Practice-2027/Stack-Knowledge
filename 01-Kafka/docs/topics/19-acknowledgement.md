# 19. Acknowledgement

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

The producer waits for metadata using flush(timeout=3) and future.get(timeout=3). No explicit acks setting is configured, so the client/library default applies. Do not describe the project as using a deliberate acks=all policy unless you configure it.

## Workflow

```text
Send -> flush -> future result -> success or exception.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

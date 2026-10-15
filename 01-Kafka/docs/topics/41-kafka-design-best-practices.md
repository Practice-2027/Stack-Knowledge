# 41. Kafka Design Best Practices

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

Good next steps are stable topic names, deliberate partition counts, keys for ordering, bounded message sizes, retries, dead-letter topics, idempotent handlers, schema validation, and lag monitoring. In this project, start with atomic result writes and a real durable database.

## Workflow

```text
Design topic -> choose key/partitions -> validate -> process safely -> observe.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

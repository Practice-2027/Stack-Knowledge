# 9. Kafka Message Structure

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

A project record contains task_id, task_name, priority, status, submitted_at, completed_at, duration_seconds, and result_message. The Kafka key is not supplied, so the producer does not intentionally choose a partition by business key. Kafka metadata adds partition and offset outside the value.

## Workflow

```text
Value fields -> serialized JSON -> Kafka record -> worker deserializes to a dictionary.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

# 49. Interview Questions

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

Beginner interview answers should be project-specific: Kafka decouples Flask from slow work; task-queue is the topic; task-processor-group shares partitions; offsets track progress; JSON is the wire format; auto-commit means duplicates are possible; one broker is a single point of failure.

## Workflow

```text
Answer what this code does before describing ideal Kafka behavior.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

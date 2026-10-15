# 31. Debugging Guide

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

For connection errors, check Docker and 9092. For no messages, check topic, group, offsets, and whether another consumer already owns the partition. Duplicate messages can follow a crash before auto-commit. Ordering is only per partition. Topic existence can be checked with kafka-topics --describe.

## Workflow

```text
Observe logs first; verify broker, topic, group, partition, and files.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

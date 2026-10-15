# 51. Common Beginner Confusions

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

Kafka is not the database or API. A topic is not a table; a partition is not a topic; a group is not one consumer; reading does not immediately delete a record; two different groups can read the same record; duplicates are possible; offsets enable restart and replay.

## Workflow

```text
If confused, return to: durable log + partitions + consumer progress.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

# 11. Partitions

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

A partition is an ordered append-only lane. This project does not explicitly create or configure partitions, so Kafka's default topic creation behavior applies. The Docker broker enables auto topic creation. Verify the real count with kafka-topics --describe.

## Workflow

```text
Record -> partition selection -> increasing offset within that partition.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

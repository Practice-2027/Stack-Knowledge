# 24. Complete Message Lifecycle

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

One task starts as HTTP JSON, receives a generated ID and QUEUED status, is serialized, stored in task-queue, assigned partition/offset, fetched by the consumer, deserialized, marked PROCESSING, simulated, marked COMPLETED, and merged back into submitted_tasks.json for the dashboard.

## Workflow

```text
Created -> producer -> serializer -> broker/topic/partition/offset -> consumer -> processing -> result -> UI.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

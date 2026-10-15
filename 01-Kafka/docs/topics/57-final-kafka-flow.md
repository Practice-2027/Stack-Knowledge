# 57. Final Kafka Flow

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

The master flow is: user/application -> Flask producer -> JSON serialization -> broker -> task-queue -> partition/offset -> consumer group -> consumer -> JSON deserialization -> processing -> result file -> dashboard. The configured system has one broker and one normal worker.

## Workflow

```text
This is the complete mental model for the repository.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

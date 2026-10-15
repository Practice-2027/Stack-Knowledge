# 22. Project Configuration and Environment Variables

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

Configuration is read mostly from code and environment. producer.py and consumer.py use KAFKA_BOOTSTRAP_SERVERS, defaulting to localhost:9092. The topic and group are constants. Docker Compose defines ports, listeners, ZooKeeper, auto topic creation, and single-replica internal settings.

## Workflow

```text
Environment/defaults -> Kafka client configuration -> broker connection -> topic/group behavior.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

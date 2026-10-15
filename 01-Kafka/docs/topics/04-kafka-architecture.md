# 4. Kafka Architecture

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

The running topology is one Docker broker and one ZooKeeper service. The topic is task-queue. The consumer group has one worker process in the normal setup. Replication and multiple brokers are not configured for this beginner project.

## Workflow

```text
Flask producer -> broker -> task-queue partition -> task-processor-group -> consumer worker.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

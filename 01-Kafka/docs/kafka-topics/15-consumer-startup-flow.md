# 15. Consumer Startup Flow

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

The consumer connects to localhost:9092, joins task-processor-group, and subscribes by passing task-queue to KafkaConsumer. The iterator over consumer continuously obtains records; consumer_timeout_ms=1000 lets the loop regain control when no record arrives.

## Workflow

```text
Create -> join group -> subscribe -> fetch/iterate -> process.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

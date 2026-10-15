# 5. Complete Project Workflow

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

At startup, producer.py loads submitted_tasks.json and tries to create KafkaProducer. consumer.py creates KafkaConsumer with auto_offset_reset=earliest and enable_auto_commit=True. On a task request, the producer sends JSON; the worker processes it for 2, 3.5, or 5 seconds depending on priority.

## Workflow

```text
Start Docker -> start consumer -> start Flask -> submit task -> send -> consume -> process -> write result -> dashboard refresh.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

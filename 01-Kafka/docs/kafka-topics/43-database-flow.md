# 43. Database Flow

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

There is no database. submitted_tasks.json and task_results.json are local files, and queue_buffer.json is a fallback queue. This is useful for learning but unsafe for multiple processes, crashes during writes, and horizontal scaling.

## Workflow

```text
Consumer -> atomic JSON result file -> producer merges -> dashboard.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

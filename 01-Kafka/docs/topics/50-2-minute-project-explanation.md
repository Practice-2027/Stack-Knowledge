# 50. 2-Minute Project Explanation

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

Two-minute answer: This project is a Flask task queue. A user submits a task; producer.py validates it, assigns an ID, serializes JSON, and sends it to task-queue. consumer.py, in task-processor-group, reads it, simulates priority-based work, and writes status to task_results.json. The dashboard polls Flask to show progress. It is a learning system, not a production cluster.

## Workflow

```text
Keep the interview story: problem -> producer -> Kafka -> consumer -> outcome.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

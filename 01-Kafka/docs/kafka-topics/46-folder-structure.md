# 46. Folder Structure

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

The repository is small: producer.py, consumer.py, docker-compose.yml, requirements.txt, templates/dashboard.html, and JSON state files. __pycache__ is generated runtime output. README.md is existing project guidance.

## Workflow

```text
Infrastructure + producer + consumer + UI + local state.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

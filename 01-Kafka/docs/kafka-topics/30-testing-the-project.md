# 30. Testing the Project

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

Test path: start Compose, run consumer.py, run producer.py, open localhost:5001, submit a task, watch QUEUED become PROCESSING and COMPLETED, then call GET /tasks. The CLI also supports POST /submit-task and GET /health.

## Workflow

```text
Infrastructure -> worker -> API -> event -> result -> dashboard.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

# 25. Error Handling

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

Implemented handling includes producer retries during connection, send exceptions with local queue_buffer.json fallback, consumer reconnect attempts, atomic result-file replacement, and graceful Ctrl+C shutdown. Invalid task_name returns HTTP 400; invalid priority becomes MEDIUM. There is no dead-letter topic or retry topic.

## Workflow

```text
Failure -> log -> retry, local buffer, or task remains dependent on persisted state.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

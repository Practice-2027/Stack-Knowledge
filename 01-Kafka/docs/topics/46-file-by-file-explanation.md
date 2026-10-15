# 46. File-by-File Explanation

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

producer.py owns HTTP and publishing; consumer.py owns polling and work; docker-compose.yml owns Kafka infrastructure; dashboard.html owns browser rendering and five-second polling; requirements.txt owns Python dependencies; JSON files hold demo state.

## Workflow

```text
Entry point -> imported library -> Kafka/file side effect -> next component.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

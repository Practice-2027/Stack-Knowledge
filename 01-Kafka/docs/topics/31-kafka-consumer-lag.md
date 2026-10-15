# 31. Kafka Consumer Lag

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

Lag is produced records minus consumed progress. The code does not expose a lag metric, but Kafka CLI or monitoring tools can measure it. Lag grows when task processing is slower than production, especially because the simulated worker handles one message at a time.

## Workflow

```text
More input than processing capacity -> backlog -> lag.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

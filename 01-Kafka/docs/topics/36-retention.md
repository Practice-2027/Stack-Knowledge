# 36. Retention

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

Kafka does not delete a record when this consumer reads it. Retention is broker policy. This Compose file does not set application retention values. Retention makes replay possible, unlike a simple destructive queue.

## Workflow

```text
Write -> retain by time/size -> consumer reads -> record remains until retention removes it.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

# 14. Kafka Consumer

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

consumer.py is the worker. It creates KafkaConsumer with the topic, bootstrap server, group_id, JSON value_deserializer, earliest reset, and automatic commits. For each message it calls process_task().

## Workflow

```text
Broker record -> message.value -> process_task -> result file.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

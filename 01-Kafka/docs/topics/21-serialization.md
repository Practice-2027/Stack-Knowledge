# 21. Serialization

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

Producer values use json.dumps(v).encode('utf-8'); consumer values use json.loads(m.decode('utf-8')). This is application-level JSON serialization, not Avro or a schema registry.

## Workflow

```text
Python dict -> JSON text -> UTF-8 bytes -> Kafka -> UTF-8 decode -> Python dict.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

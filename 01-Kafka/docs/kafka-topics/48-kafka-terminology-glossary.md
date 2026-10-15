# 48. Kafka Terminology Glossary

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

Core terms: broker is a Kafka server; topic is a named log; partition is an ordered lane; offset is a position; producer writes; consumer reads; group shares work; retention controls lifetime; lag is unprocessed distance; serialization converts objects to bytes; rebalancing redistributes partitions.

## Workflow

```text
Use the glossary to translate Kafka words into project actions.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

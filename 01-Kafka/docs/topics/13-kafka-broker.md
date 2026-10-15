# 13. Kafka Broker

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

The broker is the Kafka server in the container named kafka-broker. Host applications use localhost:9092; Docker-internal clients would use kafka:29092. One broker is configured, with single-replica internal topics.

## Workflow

```text
Producer/consumer TCP connection -> broker log -> response or fetched records.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

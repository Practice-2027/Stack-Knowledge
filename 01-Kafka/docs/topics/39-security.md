# 39. Security

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

No authentication, authorization, TLS, SASL, or secret manager is configured. The broker uses PLAINTEXT. Environment variables only override the bootstrap address. Production should protect credentials, encrypt traffic, restrict ACLs, and avoid secrets in source files.

## Workflow

```text
Current: trusted local network. Production: identity + encryption + ACLs.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

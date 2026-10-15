# 6. Kafka Producer

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

producer.py is the producer. get_kafka_producer() configures bootstrap_servers, JSON value_serializer, request timeout, and retries. submit_task() creates the task payload and calls producer.send('task-queue', value=task_payload).

## Workflow

```text
HTTP input -> validate -> create TASK-XXXXXXXX -> serialize -> send -> flush -> future.get metadata.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

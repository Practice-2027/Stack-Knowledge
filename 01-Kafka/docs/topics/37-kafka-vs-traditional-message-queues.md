# 37. Kafka vs Traditional Message Queues

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

Kafka favors durable logs, replay, partitions, and high throughput. RabbitMQ-style queues often emphasize routing and work-queue delivery. Choose Kafka for streams and replay; choose a traditional queue for simpler command delivery when replay and partition scaling are not central.

## Workflow

```text
Compare ordering, replay, retention, consumer groups, and throughput.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

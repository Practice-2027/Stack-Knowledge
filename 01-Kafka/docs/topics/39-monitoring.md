# 39. Monitoring

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

The code logs connections, sends, partitions, offsets, and task results, but it does not expose broker health, consumer lag, throughput, disk, or under-replicated partition metrics. Recommended tools include Kafka UI, JMX exporters, Prometheus, and Grafana.

## Workflow

```text
Instrument producer, broker, consumer, and business outcomes.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

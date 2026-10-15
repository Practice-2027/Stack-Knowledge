# 35. Kafka Replication

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

Replication is not meaningfully implemented here: one broker and replication factors of 1 are configured. In production, a partition has a leader and followers; ISR members replicate it, and a healthy follower can become leader after failure.

## Workflow

```text
Leader accepts writes -> followers replicate -> failover if leader fails.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

# 3. Real-Life Analogy

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

Think of an airport baggage system. The Flask producer is check-in, Kafka is the conveyor system, task-queue is a labeled belt, a partition is a lane, the consumer is a baggage worker, and an offset is the bag position. The analogy stops at delivery details: Kafka retains records and supports replay; luggage systems usually do not.

## Workflow

```text
Check in task -> label JSON -> conveyor stores it -> worker takes it -> worker records completion.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

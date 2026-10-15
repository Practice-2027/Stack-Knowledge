# 34. Scalability

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

Throughput growth requires more partitions, consumers, brokers, and storage. A group can parallelize only up to the number of partitions. This project has one worker loop and no throughput or lag monitoring, so it is a learning-scale system.

## Workflow

```text
Increase partitions -> add group members -> distribute work -> monitor lag.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

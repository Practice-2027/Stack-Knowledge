# 16. Consumer Groups

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

A consumer group lets workers share partitions. In this project the group is task-processor-group. With one partition, only one member can actively own that partition at a time. Running another consumer with the same group shares work only when enough partitions exist.

## Workflow

```text
Group coordinator assigns partitions -> one member reads each assigned partition.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

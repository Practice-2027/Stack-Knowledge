# 17. Offset

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

An offset is the position of a record within a partition. consumer.py prints message.partition and message.offset. enable_auto_commit=True commits offsets automatically about every 1000 ms. A crash around processing and commit can cause reprocessing, so this is not exactly-once.

## Workflow

```text
Fetch offset N -> process -> auto commit later -> restart resumes from committed position.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

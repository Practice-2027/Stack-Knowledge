# 12. Message Key

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

No key argument is passed to producer.send(). Therefore task identity or priority is not used to guarantee same-partition ordering. If keyed ordering is needed, send key=task_id or another stable business key and plan partitions deliberately.

## Workflow

```text
No explicit key -> Kafka's default partitioner behavior -> chosen partition.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

# 44. Complete Architecture Diagram

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

A faithful architecture is: browser/API -> Flask producer -> JSON serializer -> Kafka broker -> task-queue -> partition -> task-processor-group -> consumer.py -> task_results.json -> Flask sync -> dashboard. The fallback branch writes queue_buffer.json when Kafka send fails.

## Workflow

```text
Normal path and fallback path are both explicit in the code.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

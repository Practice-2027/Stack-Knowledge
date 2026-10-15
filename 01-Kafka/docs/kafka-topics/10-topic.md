# 10. Topic

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

task-queue is the only application topic named in the code. The producer writes to it and the consumer subscribes to it. Multiple producers could publish to it; consumers in different groups could independently read it.

## Workflow

```text
Topic name is a constant in both producer.py and consumer.py.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

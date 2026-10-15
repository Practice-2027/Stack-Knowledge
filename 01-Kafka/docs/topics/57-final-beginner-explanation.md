# 57. Final Beginner Explanation

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

Remember: a user submits a task to Flask. Flask puts a JSON event into Kafka. Kafka stores it in a topic partition with an offset. The consumer reads it, performs work, and records the result. The dashboard learns the result by polling Flask. Kafka makes the slow work asynchronous.

## Workflow

```text
Short memory aid: submit -> store -> read -> work -> record -> display.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

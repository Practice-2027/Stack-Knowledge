# 56. PDF Quality Check

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

Quality checks include generated page count, extractable text, section presence, output file existence, and PNG rendering of representative pages. Visual inspection should confirm headings, wrapping, footer numbers, and diagrams are readable.

## Workflow

```text
Generate -> render -> inspect -> fix -> deliver.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

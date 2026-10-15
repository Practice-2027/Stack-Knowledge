# 55. PDF Document

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

The PDF is a formatted study guide with title page, contents, project facts, and one topic section per numbered requirement. It includes readable workflows, code references, commands, and production notes.

## Workflow

```text
Markdown content -> ReportLab styles -> page breaks -> validated PDF.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

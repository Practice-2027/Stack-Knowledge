# 18. Consumer Polling

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

The kafka-python consumer pulls records by iterating over KafkaConsumer. Kafka does not call process_task directly; the client fetches batches or records from the broker. This allows the consumer to control its pace and apply backpressure.

## Workflow

```text
Consumer fetch request -> broker returns available records -> iterator yields message.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

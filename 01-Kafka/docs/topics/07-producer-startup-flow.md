# 7. Producer Startup Flow

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

The producer is created lazily and cached in producer_instance. Startup attempts two connections; a request can make a one-attempt connection. If the broker is still starting, NoBrokersAvailable is logged and the local fallback may be used.

## Workflow

```text
Create client -> connect to localhost:9092 -> keep client -> reuse for requests.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

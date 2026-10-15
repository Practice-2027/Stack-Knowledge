# 29. Kafka CLI Commands

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

Useful commands are: docker compose up -d; docker compose ps; docker exec -it kafka-broker kafka-topics --bootstrap-server localhost:9092 --list; --describe --topic task-queue; kafka-console-consumer --topic task-queue --from-beginning; docker compose down. Use the container's CLI so versions match.

## Workflow

```text
Start -> inspect -> create/describe -> produce/consume -> stop.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

# 24. Complete Code Execution Flow

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

The main functions are producer.py: load_persisted_tasks(), get_kafka_producer(), submit_task(); and consumer.py: create_kafka_consumer(), process_task(), main(). The actual call chain is Flask route -> producer.send -> Kafka -> consumer iterator -> process_task -> update_task_results.

## Workflow

```text
main/app.run -> route -> send; main -> consumer -> process_task.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

# 45. Sequence Diagram

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Beginner meaning

Sequence: client POSTs; Flask validates and creates payload; producer sends; broker assigns metadata; consumer fetches; worker marks PROCESSING; worker sleeps through three stages; worker writes COMPLETED; dashboard polls GET /tasks. The original POST does not wait for completion.

## Workflow

```text
POST -> send -> fetch -> process -> persist -> poll.
```

## What is implemented

The statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.

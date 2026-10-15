# Complete Kafka Documentation - Beginner to Project to Production

Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json and task_results.json.

## Contents

1. [Project Overview](topics/01-project-overview.md)
2. [What Is Kafka?](topics/02-what-is-kafka.md)
3. [Real-Life Analogy](topics/03-real-life-analogy.md)
4. [Kafka Architecture](topics/04-kafka-architecture.md)
5. [Complete Project Workflow](topics/05-complete-project-workflow.md)
6. [Kafka Producer](topics/06-kafka-producer.md)
7. [Producer Startup Flow](topics/07-producer-startup-flow.md)
8. [Producer Message Flow](topics/08-producer-message-flow.md)
9. [Kafka Message Structure](topics/09-kafka-message-structure.md)
10. [Topic](topics/10-topic.md)
11. [Partitions](topics/11-partitions.md)
12. [Message Key](topics/12-message-key.md)
13. [Kafka Broker](topics/13-kafka-broker.md)
14. [Kafka Consumer](topics/14-kafka-consumer.md)
15. [Consumer Startup Flow](topics/15-consumer-startup-flow.md)
16. [Consumer Groups](topics/16-consumer-groups.md)
17. [Offset](topics/17-offset.md)
18. [Consumer Polling](topics/18-consumer-polling.md)
19. [Acknowledgement](topics/19-acknowledgement.md)
20. [Message Delivery](topics/20-message-delivery.md)
21. [Serialization](topics/21-serialization.md)
22. [Project Configuration and Environment Variables](topics/22-project-configuration-and-environment-variables.md)
23. [Request/Response vs Kafka](topics/23-request-response-vs-kafka.md)
24. [Complete Message Lifecycle](topics/24-complete-message-lifecycle.md)
25. [Complete Code Execution Flow](topics/25-complete-code-execution-flow.md)
26. [Error Handling](topics/26-error-handling.md)
27. [Kafka Docker Setup](topics/27-kafka-docker-setup.md)
28. [ZooKeeper vs KRaft](topics/28-zookeeper-vs-kraft.md)
29. [Kafka CLI Commands](topics/29-kafka-cli-commands.md)
30. [Testing the Project](topics/30-testing-the-project.md)
31. [Debugging Guide](topics/31-debugging-guide.md)
32. [Kafka Consumer Lag](topics/32-kafka-consumer-lag.md)
33. [Beginner Project to Real Project](topics/33-beginner-project-to-real-project.md)
34. [Real-World Use Cases](topics/34-real-world-use-cases.md)
35. [Scalability](topics/35-scalability.md)
36. [Kafka Replication](topics/36-kafka-replication.md)
37. [Retention](topics/37-retention.md)
38. [Kafka vs Traditional Message Queues](topics/38-kafka-vs-traditional-message-queues.md)
39. [Security](topics/39-security.md)
40. [Monitoring](topics/40-monitoring.md)
41. [Kafka Design Best Practices](topics/41-kafka-design-best-practices.md)
42. [Complete API Flow](topics/42-complete-api-flow.md)
43. [Database Flow](topics/43-database-flow.md)
44. [Complete Architecture Diagram](topics/44-complete-architecture-diagram.md)
45. [Sequence Diagram](topics/45-sequence-diagram.md)
46. [Folder Structure](topics/46-folder-structure.md)
47. [File-by-File Explanation](topics/47-file-by-file-explanation.md)
48. [Kafka Terminology Glossary](topics/48-kafka-terminology-glossary.md)
49. [Interview Questions](topics/49-interview-questions.md)
50. [2-Minute Project Explanation](topics/50-2-minute-project-explanation.md)
51. [5-Minute Technical Explanation](topics/51-5-minute-technical-explanation.md)
52. [Common Beginner Confusions](topics/52-common-beginner-confusions.md)
53. [Documentation Files](topics/53-documentation-files.md)
54. [Master Markdown File](topics/54-master-markdown-file.md)
55. [PDF Document](topics/55-pdf-document.md)
56. [PDF Quality Check](topics/56-pdf-quality-check.md)
57. [Final Kafka Flow](topics/57-final-kafka-flow.md)
58. [Final Beginner Explanation](topics/58-final-beginner-explanation.md)
59. [Final Project Report](topics/59-final-project-report.md)
60. [Most Important Rule: One Message](topics/60-most-important-rule-one-message.md)

## Project truth

This documentation is based on the files present in this repository. When a feature is absent, it is marked as not implemented rather than assumed.

## 1. Project Overview

This is an asynchronous task queue. A browser calls Flask, Flask creates a task record and publishes JSON to Kafka, and consumer.py processes it in the background. The dashboard reads local JSON state to show QUEUED, PROCESSING, or COMPLETED.

### Workflow

```text
User -> POST /submit-task -> producer.py -> task-queue -> consumer.py -> task_results.json -> GET /tasks -> dashboard
```

## 2. What Is Kafka?

Kafka is a durable, distributed log. It lets the web request finish quickly while another process handles slow work later. In this project Kafka separates the Flask web server from the worker.

### Workflow

```text
Without Kafka: browser waits for work. With Kafka: browser submits an event, Kafka stores it, and the worker reads it when ready.
```

## 3. Real-Life Analogy

Think of an airport baggage system. The Flask producer is check-in, Kafka is the conveyor system, task-queue is a labeled belt, a partition is a lane, the consumer is a baggage worker, and an offset is the bag position. The analogy stops at delivery details: Kafka retains records and supports replay; luggage systems usually do not.

### Workflow

```text
Check in task -> label JSON -> conveyor stores it -> worker takes it -> worker records completion.
```

## 4. Kafka Architecture

The running topology is one Docker broker and one ZooKeeper service. The topic is task-queue. The consumer group has one worker process in the normal setup. Replication and multiple brokers are not configured for this beginner project.

### Workflow

```text
Flask producer -> broker -> task-queue partition -> task-processor-group -> consumer worker.
```

## 5. Complete Project Workflow

At startup, producer.py loads submitted_tasks.json and tries to create KafkaProducer. consumer.py creates KafkaConsumer with auto_offset_reset=earliest and enable_auto_commit=True. On a task request, the producer sends JSON; the worker processes it for 2, 3.5, or 5 seconds depending on priority.

### Workflow

```text
Start Docker -> start consumer -> start Flask -> submit task -> send -> consume -> process -> write result -> dashboard refresh.
```

## 6. Kafka Producer

producer.py is the producer. get_kafka_producer() configures bootstrap_servers, JSON value_serializer, request timeout, and retries. submit_task() creates the task payload and calls producer.send('task-queue', value=task_payload).

### Workflow

```text
HTTP input -> validate -> create TASK-XXXXXXXX -> serialize -> send -> flush -> future.get metadata.
```

## 7. Producer Startup Flow

The producer is created lazily and cached in producer_instance. Startup attempts two connections; a request can make a one-attempt connection. If the broker is still starting, NoBrokersAvailable is logged and the local fallback may be used.

### Workflow

```text
Create client -> connect to localhost:9092 -> keep client -> reuse for requests.
```

## 8. Producer Message Flow

producer.send() passes a Python dictionary to the JSON serializer. Kafka receives bytes, assigns a partition and offset, and future.get() returns metadata. The code logs topic, partition, and offset after flush and acknowledgement.

### Workflow

```text
Dictionary -> JSON UTF-8 bytes -> broker -> partition/offset -> producer metadata.
```

## 9. Kafka Message Structure

A project record contains task_id, task_name, priority, status, submitted_at, completed_at, duration_seconds, and result_message. The Kafka key is not supplied, so the producer does not intentionally choose a partition by business key. Kafka metadata adds partition and offset outside the value.

### Workflow

```text
Value fields -> serialized JSON -> Kafka record -> worker deserializes to a dictionary.
```

## 10. Topic

task-queue is the only application topic named in the code. The producer writes to it and the consumer subscribes to it. Multiple producers could publish to it; consumers in different groups could independently read it.

### Workflow

```text
Topic name is a constant in both producer.py and consumer.py.
```

## 11. Partitions

A partition is an ordered append-only lane. This project does not explicitly create or configure partitions, so Kafka's default topic creation behavior applies. The Docker broker enables auto topic creation. Verify the real count with kafka-topics --describe.

### Workflow

```text
Record -> partition selection -> increasing offset within that partition.
```

## 12. Message Key

No key argument is passed to producer.send(). Therefore task identity or priority is not used to guarantee same-partition ordering. If keyed ordering is needed, send key=task_id or another stable business key and plan partitions deliberately.

### Workflow

```text
No explicit key -> Kafka's default partitioner behavior -> chosen partition.
```

## 13. Kafka Broker

The broker is the Kafka server in the container named kafka-broker. Host applications use localhost:9092; Docker-internal clients would use kafka:29092. One broker is configured, with single-replica internal topics.

### Workflow

```text
Producer/consumer TCP connection -> broker log -> response or fetched records.
```

## 14. Kafka Consumer

consumer.py is the worker. It creates KafkaConsumer with the topic, bootstrap server, group_id, JSON value_deserializer, earliest reset, and automatic commits. For each message it calls process_task().

### Workflow

```text
Broker record -> message.value -> process_task -> result file.
```

## 15. Consumer Startup Flow

The consumer connects to localhost:9092, joins task-processor-group, and subscribes by passing task-queue to KafkaConsumer. The iterator over consumer continuously obtains records; consumer_timeout_ms=1000 lets the loop regain control when no record arrives.

### Workflow

```text
Create -> join group -> subscribe -> fetch/iterate -> process.
```

## 16. Consumer Groups

A consumer group lets workers share partitions. In this project the group is task-processor-group. With one partition, only one member can actively own that partition at a time. Running another consumer with the same group shares work only when enough partitions exist.

### Workflow

```text
Group coordinator assigns partitions -> one member reads each assigned partition.
```

## 17. Offset

An offset is the position of a record within a partition. consumer.py prints message.partition and message.offset. enable_auto_commit=True commits offsets automatically about every 1000 ms. A crash around processing and commit can cause reprocessing, so this is not exactly-once.

### Workflow

```text
Fetch offset N -> process -> auto commit later -> restart resumes from committed position.
```

## 18. Consumer Polling

The kafka-python consumer pulls records by iterating over KafkaConsumer. Kafka does not call process_task directly; the client fetches batches or records from the broker. This allows the consumer to control its pace and apply backpressure.

### Workflow

```text
Consumer fetch request -> broker returns available records -> iterator yields message.
```

## 19. Acknowledgement

The producer waits for metadata using flush(timeout=3) and future.get(timeout=3). No explicit acks setting is configured, so the client/library default applies. Do not describe the project as using a deliberate acks=all policy unless you configure it.

### Workflow

```text
Send -> flush -> future result -> success or exception.
```

## 20. Message Delivery

The intended normal path is at-least-once-like: a record can be processed and then seen again if the process fails before its automatic offset commit. Exactly-once is not implemented. At-most-once is not intentionally configured either.

### Workflow

```text
Delivery guarantee depends on commit timing and worker failure.
```

## 21. Serialization

Producer values use json.dumps(v).encode('utf-8'); consumer values use json.loads(m.decode('utf-8')). This is application-level JSON serialization, not Avro or a schema registry.

### Workflow

```text
Python dict -> JSON text -> UTF-8 bytes -> Kafka -> UTF-8 decode -> Python dict.
```

## 22. Project Configuration and Environment Variables

Configuration is read mostly from code and environment. producer.py and consumer.py use KAFKA_BOOTSTRAP_SERVERS, defaulting to localhost:9092. The topic and group are constants. Docker Compose defines ports, listeners, ZooKeeper, auto topic creation, and single-replica internal settings.

### Workflow

```text
Environment/defaults -> Kafka client configuration -> broker connection -> topic/group behavior.
```

## 23. Request/Response vs Kafka

REST is synchronous request/response: the caller waits for a response. Kafka is asynchronous: the producer publishes an event and the consumer processes it later. This project uses REST for submission and status queries, Kafka for background task transport.

### Workflow

```text
POST submits intent; GET /tasks reads local status; Kafka carries work.
```

## 24. Complete Message Lifecycle

One task starts as HTTP JSON, receives a generated ID and QUEUED status, is serialized, stored in task-queue, assigned partition/offset, fetched by the consumer, deserialized, marked PROCESSING, simulated, marked COMPLETED, and merged back into submitted_tasks.json for the dashboard.

### Workflow

```text
Created -> producer -> serializer -> broker/topic/partition/offset -> consumer -> processing -> result -> UI.
```

## 25. Complete Code Execution Flow

The main functions are producer.py: load_persisted_tasks(), get_kafka_producer(), submit_task(); and consumer.py: create_kafka_consumer(), process_task(), main(). The actual call chain is Flask route -> producer.send -> Kafka -> consumer iterator -> process_task -> update_task_results.

### Workflow

```text
main/app.run -> route -> send; main -> consumer -> process_task.
```

## 26. Error Handling

Implemented handling includes producer retries during connection, send exceptions with local queue_buffer.json fallback, consumer reconnect attempts, atomic result-file replacement, and graceful Ctrl+C shutdown. Invalid task_name returns HTTP 400; invalid priority becomes MEDIUM. There is no dead-letter topic or retry topic.

### Workflow

```text
Failure -> log -> retry, local buffer, or task remains dependent on persisted state.
```

## 27. Kafka Docker Setup

docker-compose.yml runs cp-zookeeper:7.5.0 on 2181 and cp-kafka:7.5.0 on 9092. It advertises localhost:9092 for host scripts and kafka:29092 internally, enables auto topic creation, and uses one broker. Volumes are not declared, so persistence is not explicitly configured.

### Workflow

```text
docker compose up -d -> ZooKeeper -> broker -> Python clients.
```

## 28. ZooKeeper vs KRaft

This project uses ZooKeeper through KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181. It does not use KRaft. KRaft is Kafka's newer metadata mode; migration would require a different Compose configuration and is outside the current implementation.

### Workflow

```text
ZooKeeper coordinates broker metadata; broker serves records.
```

## 29. Kafka CLI Commands

Useful commands are: docker compose up -d; docker compose ps; docker exec -it kafka-broker kafka-topics --bootstrap-server localhost:9092 --list; --describe --topic task-queue; kafka-console-consumer --topic task-queue --from-beginning; docker compose down. Use the container's CLI so versions match.

### Workflow

```text
Start -> inspect -> create/describe -> produce/consume -> stop.
```

## 30. Testing the Project

Test path: start Compose, run consumer.py, run producer.py, open localhost:5001, submit a task, watch QUEUED become PROCESSING and COMPLETED, then call GET /tasks. The CLI also supports POST /submit-task and GET /health.

### Workflow

```text
Infrastructure -> worker -> API -> event -> result -> dashboard.
```

## 31. Debugging Guide

For connection errors, check Docker and 9092. For no messages, check topic, group, offsets, and whether another consumer already owns the partition. Duplicate messages can follow a crash before auto-commit. Ordering is only per partition. Topic existence can be checked with kafka-topics --describe.

### Workflow

```text
Observe logs first; verify broker, topic, group, partition, and files.
```

## 32. Kafka Consumer Lag

Lag is produced records minus consumed progress. The code does not expose a lag metric, but Kafka CLI or monitoring tools can measure it. Lag grows when task processing is slower than production, especially because the simulated worker handles one message at a time.

### Workflow

```text
More input than processing capacity -> backlog -> lag.
```

## 33. Beginner Project to Real Project

The beginner stage is Flask -> one Kafka topic -> one worker. An intermediate system adds APIs, multiple consumer groups, and a database. Production adds multiple brokers, replication, observability, schema governance, security, and separate topics for business events.

### Workflow

```text
Scale by separating request handling, transport, workers, and storage.
```

## 34. Real-World Use Cases

Examples map directly to the same pattern: orders producer -> orders topic -> fulfillment consumer; payment event -> payment topic -> notification consumer; logs -> log topic -> analytics consumer. The current project specifically represents background task execution.

### Workflow

```text
Event producer -> named topic -> specialized consumer group.
```

## 35. Scalability

Throughput growth requires more partitions, consumers, brokers, and storage. A group can parallelize only up to the number of partitions. This project has one worker loop and no throughput or lag monitoring, so it is a learning-scale system.

### Workflow

```text
Increase partitions -> add group members -> distribute work -> monitor lag.
```

## 36. Kafka Replication

Replication is not meaningfully implemented here: one broker and replication factors of 1 are configured. In production, a partition has a leader and followers; ISR members replicate it, and a healthy follower can become leader after failure.

### Workflow

```text
Leader accepts writes -> followers replicate -> failover if leader fails.
```

## 37. Retention

Kafka does not delete a record when this consumer reads it. Retention is broker policy. This Compose file does not set application retention values. Retention makes replay possible, unlike a simple destructive queue.

### Workflow

```text
Write -> retain by time/size -> consumer reads -> record remains until retention removes it.
```

## 38. Kafka vs Traditional Message Queues

Kafka favors durable logs, replay, partitions, and high throughput. RabbitMQ-style queues often emphasize routing and work-queue delivery. Choose Kafka for streams and replay; choose a traditional queue for simpler command delivery when replay and partition scaling are not central.

### Workflow

```text
Compare ordering, replay, retention, consumer groups, and throughput.
```

## 39. Security

No authentication, authorization, TLS, SASL, or secret manager is configured. The broker uses PLAINTEXT. Environment variables only override the bootstrap address. Production should protect credentials, encrypt traffic, restrict ACLs, and avoid secrets in source files.

### Workflow

```text
Current: trusted local network. Production: identity + encryption + ACLs.
```

## 40. Monitoring

The code logs connections, sends, partitions, offsets, and task results, but it does not expose broker health, consumer lag, throughput, disk, or under-replicated partition metrics. Recommended tools include Kafka UI, JMX exporters, Prometheus, and Grafana.

### Workflow

```text
Instrument producer, broker, consumer, and business outcomes.
```

## 41. Kafka Design Best Practices

Good next steps are stable topic names, deliberate partition counts, keys for ordering, bounded message sizes, retries, dead-letter topics, idempotent handlers, schema validation, and lag monitoring. In this project, start with atomic result writes and a real durable database.

### Workflow

```text
Design topic -> choose key/partitions -> validate -> process safely -> observe.
```

## 42. Complete API Flow

Implemented API routes are GET /, POST /submit-task, GET /tasks, and GET /health on port 5001. POST accepts JSON or form data. It creates the event and returns 201; the consumer does not respond synchronously to the original POST.

### Workflow

```text
Client -> Flask -> Kafka -> worker -> files -> GET /tasks.
```

## 43. Database Flow

There is no database. submitted_tasks.json and task_results.json are local files, and queue_buffer.json is a fallback queue. This is useful for learning but unsafe for multiple processes, crashes during writes, and horizontal scaling.

### Workflow

```text
Consumer -> atomic JSON result file -> producer merges -> dashboard.
```

## 44. Complete Architecture Diagram

A faithful architecture is: browser/API -> Flask producer -> JSON serializer -> Kafka broker -> task-queue -> partition -> task-processor-group -> consumer.py -> task_results.json -> Flask sync -> dashboard. The fallback branch writes queue_buffer.json when Kafka send fails.

### Workflow

```text
Normal path and fallback path are both explicit in the code.
```

## 45. Sequence Diagram

Sequence: client POSTs; Flask validates and creates payload; producer sends; broker assigns metadata; consumer fetches; worker marks PROCESSING; worker sleeps through three stages; worker writes COMPLETED; dashboard polls GET /tasks. The original POST does not wait for completion.

### Workflow

```text
POST -> send -> fetch -> process -> persist -> poll.
```

## 46. Folder Structure

The repository is small: producer.py, consumer.py, docker-compose.yml, requirements.txt, templates/dashboard.html, and JSON state files. __pycache__ is generated runtime output. README.md is existing project guidance.

### Workflow

```text
Infrastructure + producer + consumer + UI + local state.
```

## 47. File-by-File Explanation

producer.py owns HTTP and publishing; consumer.py owns polling and work; docker-compose.yml owns Kafka infrastructure; dashboard.html owns browser rendering and five-second polling; requirements.txt owns Python dependencies; JSON files hold demo state.

### Workflow

```text
Entry point -> imported library -> Kafka/file side effect -> next component.
```

## 48. Kafka Terminology Glossary

Core terms: broker is a Kafka server; topic is a named log; partition is an ordered lane; offset is a position; producer writes; consumer reads; group shares work; retention controls lifetime; lag is unprocessed distance; serialization converts objects to bytes; rebalancing redistributes partitions.

### Workflow

```text
Use the glossary to translate Kafka words into project actions.
```

## 49. Interview Questions

Beginner interview answers should be project-specific: Kafka decouples Flask from slow work; task-queue is the topic; task-processor-group shares partitions; offsets track progress; JSON is the wire format; auto-commit means duplicates are possible; one broker is a single point of failure.

### Workflow

```text
Answer what this code does before describing ideal Kafka behavior.
```

## 50. 2-Minute Project Explanation

Two-minute answer: This project is a Flask task queue. A user submits a task; producer.py validates it, assigns an ID, serializes JSON, and sends it to task-queue. consumer.py, in task-processor-group, reads it, simulates priority-based work, and writes status to task_results.json. The dashboard polls Flask to show progress. It is a learning system, not a production cluster.

### Workflow

```text
Keep the interview story: problem -> producer -> Kafka -> consumer -> outcome.
```

## 51. 5-Minute Technical Explanation

Five-minute answer should add broker localhost:9092, one topic, group_id, partition/offset metadata, earliest reset, automatic commits, status transitions, JSON serializer/deserializer, retries, fallback buffer, and the limitations of local files and one broker.

### Workflow

```text
Expand the two-minute story with one message's technical lifecycle.
```

## 52. Common Beginner Confusions

Kafka is not the database or API. A topic is not a table; a partition is not a topic; a group is not one consumer; reading does not immediately delete a record; two different groups can read the same record; duplicates are possible; offsets enable restart and replay.

### Workflow

```text
If confused, return to: durable log + partitions + consumer progress.
```

## 53. Documentation Files

The requested split is represented by docs/topics/01-...md through 60-...md, plus a master document. Each topic file is beginner-oriented and names the actual project files and workflow.

### Workflow

```text
Open a topic file for focused learning; use the master for the complete path.
```

## 54. Master Markdown File

The master file combines all 60 sections, the project facts, diagrams, commands, workflows, limitations, and final report. It is the easiest file to search and share as source Markdown.

### Workflow

```text
Topic pages -> ordered master Markdown -> PDF rendering.
```

## 55. PDF Document

The PDF is a formatted study guide with title page, contents, project facts, and one topic section per numbered requirement. It includes readable workflows, code references, commands, and production notes.

### Workflow

```text
Markdown content -> ReportLab styles -> page breaks -> validated PDF.
```

## 56. PDF Quality Check

Quality checks include generated page count, extractable text, section presence, output file existence, and PNG rendering of representative pages. Visual inspection should confirm headings, wrapping, footer numbers, and diagrams are readable.

### Workflow

```text
Generate -> render -> inspect -> fix -> deliver.
```

## 57. Final Kafka Flow

The master flow is: user/application -> Flask producer -> JSON serialization -> broker -> task-queue -> partition/offset -> consumer group -> consumer -> JSON deserialization -> processing -> result file -> dashboard. The configured system has one broker and one normal worker.

### Workflow

```text
This is the complete mental model for the repository.
```

## 58. Final Beginner Explanation

Remember: a user submits a task to Flask. Flask puts a JSON event into Kafka. Kafka stores it in a topic partition with an offset. The consumer reads it, performs work, and records the result. The dashboard learns the result by polling Flask. Kafka makes the slow work asynchronous.

### Workflow

```text
Short memory aid: submit -> store -> read -> work -> record -> display.
```

## 59. Final Project Report

Project: Apache Kafka Task Queue System. Language: Python. Library: Flask, kafka-python, Jinja2, colorama. Broker: localhost:9092, one Docker broker. Topic: task-queue. Group: task-processor-group. Producer: producer.py. Consumer: consumer.py. State: JSON files. API: four Flask routes. Missing: database, replication, security, schema registry, metrics, dead-letter topic, and true exactly-once processing.

### Workflow

```text
Recommended improvements: durable storage, multiple brokers, explicit partitions, secure listeners, monitoring, retries, idempotency, tests, and CI.
```

## 60. Most Important Rule: One Message

The deliverable set contains 60 topic Markdown files and one master Markdown file. The PDF is a single complete document so it can be printed or shared. Each topic is kept in the same order as the pasted requirements.

### Workflow

```text
Use individual files for focused study and the PDF for a linear course.
```

## Final project report

- Project: Apache Kafka Task Queue System
- Language: Python
- Kafka library: kafka-python
- Kafka version/image: Confluent Platform 7.5.0 container
- Broker: localhost:9092; one broker
- Topics: task-queue
- Consumer group: task-processor-group
- Producer: producer.py
- Consumer: consumer.py
- API: /, /submit-task, /tasks, /health
- State files: submitted_tasks.json, task_results.json, queue_buffer.json
- Not implemented: database, replication beyond factor 1, security, schema registry, metrics, dead-letter topic, exactly-once processing.

from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted, Table, TableStyle

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
TOPICS_DIR = DOCS / "kafka-topics"
PDF_DIR = ROOT / "output" / "pdf"
TOPICS_DIR.mkdir(parents=True, exist_ok=True)
PDF_DIR.mkdir(parents=True, exist_ok=True)

project_facts = (
    "Actual project: Python Flask producer in producer.py; kafka-python KafkaProducer; consumer worker in consumer.py; "
    "topic task-queue; broker localhost:9092 by default; consumer group task-processor-group; Docker Compose runs one "
    "Confluent Platform 7.5.0 broker plus ZooKeeper on 2181; JSON values; task status files are submitted_tasks.json "
    "and task_results.json."
)

titles = [
    "Project Overview", "What Is Kafka?", "Real-Life Analogy", "Kafka Architecture", "Complete Project Workflow",
    "Kafka Producer", "Producer Startup Flow", "Producer Message Flow", "Kafka Message Structure", "Topic",
    "Partitions", "Message Key", "Kafka Broker", "Kafka Consumer", "Consumer Startup Flow", "Consumer Groups",
    "Offset", "Consumer Polling", "Acknowledgement", "Message Delivery", "Serialization", "Request/Response vs Kafka",
    "Complete Message Lifecycle", "Complete Code Execution Flow", "Error Handling", "Kafka Docker Setup", "ZooKeeper vs KRaft",
    "Kafka CLI Commands", "Testing the Project", "Debugging Guide", "Kafka Consumer Lag", "Beginner Project to Real Project",
    "Real-World Use Cases", "Scalability", "Kafka Replication", "Retention", "Kafka vs Traditional Message Queues",
    "Security", "Monitoring", "Kafka Design Best Practices", "Complete API Flow", "Database Flow", "Complete Architecture Diagram",
    "Sequence Diagram", "Folder Structure", "File-by-File Explanation", "Kafka Terminology Glossary", "Interview Questions",
    "2-Minute Project Explanation", "5-Minute Technical Explanation", "Common Beginner Confusions", "Documentation Files",
    "Master Markdown File", "PDF Document", "PDF Quality Check", "Final Kafka Flow", "Final Beginner Explanation", "Final Project Report",
    "Most Important Rule: One Message"
]
titles.insert(21, "Project Configuration and Environment Variables")

custom = {
1: ("This is an asynchronous task queue. A browser calls Flask, Flask creates a task record and publishes JSON to Kafka, and consumer.py processes it in the background. The dashboard reads local JSON state to show QUEUED, PROCESSING, or COMPLETED.", "User -> POST /submit-task -> producer.py -> task-queue -> consumer.py -> task_results.json -> GET /tasks -> dashboard"),
2: ("Kafka is a durable, distributed log. It lets the web request finish quickly while another process handles slow work later. In this project Kafka separates the Flask web server from the worker.", "Without Kafka: browser waits for work. With Kafka: browser submits an event, Kafka stores it, and the worker reads it when ready."),
3: ("Think of an airport baggage system. The Flask producer is check-in, Kafka is the conveyor system, task-queue is a labeled belt, a partition is a lane, the consumer is a baggage worker, and an offset is the bag position. The analogy stops at delivery details: Kafka retains records and supports replay; luggage systems usually do not.", "Check in task -> label JSON -> conveyor stores it -> worker takes it -> worker records completion."),
4: ("The running topology is one Docker broker and one ZooKeeper service. The topic is task-queue. The consumer group has one worker process in the normal setup. Replication and multiple brokers are not configured for this beginner project.", "Flask producer -> broker -> task-queue partition -> task-processor-group -> consumer worker."),
5: ("At startup, producer.py loads submitted_tasks.json and tries to create KafkaProducer. consumer.py creates KafkaConsumer with auto_offset_reset=earliest and enable_auto_commit=True. On a task request, the producer sends JSON; the worker processes it for 2, 3.5, or 5 seconds depending on priority.", "Start Docker -> start consumer -> start Flask -> submit task -> send -> consume -> process -> write result -> dashboard refresh."),
6: ("producer.py is the producer. get_kafka_producer() configures bootstrap_servers, JSON value_serializer, request timeout, and retries. submit_task() creates the task payload and calls producer.send('task-queue', value=task_payload).", "HTTP input -> validate -> create TASK-XXXXXXXX -> serialize -> send -> flush -> future.get metadata."),
7: ("The producer is created lazily and cached in producer_instance. Startup attempts two connections; a request can make a one-attempt connection. If the broker is still starting, NoBrokersAvailable is logged and the local fallback may be used.", "Create client -> connect to localhost:9092 -> keep client -> reuse for requests."),
8: ("producer.send() passes a Python dictionary to the JSON serializer. Kafka receives bytes, assigns a partition and offset, and future.get() returns metadata. The code logs topic, partition, and offset after flush and acknowledgement.", "Dictionary -> JSON UTF-8 bytes -> broker -> partition/offset -> producer metadata."),
9: ("A project record contains task_id, task_name, priority, status, submitted_at, completed_at, duration_seconds, and result_message. The Kafka key is not supplied, so the producer does not intentionally choose a partition by business key. Kafka metadata adds partition and offset outside the value.", "Value fields -> serialized JSON -> Kafka record -> worker deserializes to a dictionary."),
10: ("task-queue is the only application topic named in the code. The producer writes to it and the consumer subscribes to it. Multiple producers could publish to it; consumers in different groups could independently read it.", "Topic name is a constant in both producer.py and consumer.py."),
11: ("A partition is an ordered append-only lane. This project does not explicitly create or configure partitions, so Kafka's default topic creation behavior applies. The Docker broker enables auto topic creation. Verify the real count with kafka-topics --describe.", "Record -> partition selection -> increasing offset within that partition."),
12: ("No key argument is passed to producer.send(). Therefore task identity or priority is not used to guarantee same-partition ordering. If keyed ordering is needed, send key=task_id or another stable business key and plan partitions deliberately.", "No explicit key -> Kafka's default partitioner behavior -> chosen partition."),
13: ("The broker is the Kafka server in the container named kafka-broker. Host applications use localhost:9092; Docker-internal clients would use kafka:29092. One broker is configured, with single-replica internal topics.", "Producer/consumer TCP connection -> broker log -> response or fetched records."),
14: ("consumer.py is the worker. It creates KafkaConsumer with the topic, bootstrap server, group_id, JSON value_deserializer, earliest reset, and automatic commits. For each message it calls process_task().", "Broker record -> message.value -> process_task -> result file."),
15: ("The consumer connects to localhost:9092, joins task-processor-group, and subscribes by passing task-queue to KafkaConsumer. The iterator over consumer continuously obtains records; consumer_timeout_ms=1000 lets the loop regain control when no record arrives.", "Create -> join group -> subscribe -> fetch/iterate -> process."),
16: ("A consumer group lets workers share partitions. In this project the group is task-processor-group. With one partition, only one member can actively own that partition at a time. Running another consumer with the same group shares work only when enough partitions exist.", "Group coordinator assigns partitions -> one member reads each assigned partition."),
17: ("An offset is the position of a record within a partition. consumer.py prints message.partition and message.offset. enable_auto_commit=True commits offsets automatically about every 1000 ms. A crash around processing and commit can cause reprocessing, so this is not exactly-once.", "Fetch offset N -> process -> auto commit later -> restart resumes from committed position."),
18: ("The kafka-python consumer pulls records by iterating over KafkaConsumer. Kafka does not call process_task directly; the client fetches batches or records from the broker. This allows the consumer to control its pace and apply backpressure.", "Consumer fetch request -> broker returns available records -> iterator yields message."),
19: ("The producer waits for metadata using flush(timeout=3) and future.get(timeout=3). No explicit acks setting is configured, so the client/library default applies. Do not describe the project as using a deliberate acks=all policy unless you configure it.", "Send -> flush -> future result -> success or exception."),
20: ("The intended normal path is at-least-once-like: a record can be processed and then seen again if the process fails before its automatic offset commit. Exactly-once is not implemented. At-most-once is not intentionally configured either.", "Delivery guarantee depends on commit timing and worker failure."),
21: ("Producer values use json.dumps(v).encode('utf-8'); consumer values use json.loads(m.decode('utf-8')). This is application-level JSON serialization, not Avro or a schema registry.", "Python dict -> JSON text -> UTF-8 bytes -> Kafka -> UTF-8 decode -> Python dict."),
22: ("REST is synchronous request/response: the caller waits for a response. Kafka is asynchronous: the producer publishes an event and the consumer processes it later. This project uses REST for submission and status queries, Kafka for background task transport.", "POST submits intent; GET /tasks reads local status; Kafka carries work."),
23: ("One task starts as HTTP JSON, receives a generated ID and QUEUED status, is serialized, stored in task-queue, assigned partition/offset, fetched by the consumer, deserialized, marked PROCESSING, simulated, marked COMPLETED, and merged back into submitted_tasks.json for the dashboard.", "Created -> producer -> serializer -> broker/topic/partition/offset -> consumer -> processing -> result -> UI."),
24: ("The main functions are producer.py: load_persisted_tasks(), get_kafka_producer(), submit_task(); and consumer.py: create_kafka_consumer(), process_task(), main(). The actual call chain is Flask route -> producer.send -> Kafka -> consumer iterator -> process_task -> update_task_results.", "main/app.run -> route -> send; main -> consumer -> process_task."),
25: ("Implemented handling includes producer retries during connection, send exceptions with local queue_buffer.json fallback, consumer reconnect attempts, atomic result-file replacement, and graceful Ctrl+C shutdown. Invalid task_name returns HTTP 400; invalid priority becomes MEDIUM. There is no dead-letter topic or retry topic.", "Failure -> log -> retry, local buffer, or task remains dependent on persisted state."),
26: ("docker-compose.yml runs cp-zookeeper:7.5.0 on 2181 and cp-kafka:7.5.0 on 9092. It advertises localhost:9092 for host scripts and kafka:29092 internally, enables auto topic creation, and uses one broker. Volumes are not declared, so persistence is not explicitly configured.", "docker compose up -d -> ZooKeeper -> broker -> Python clients."),
27: ("This project uses ZooKeeper through KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181. It does not use KRaft. KRaft is Kafka's newer metadata mode; migration would require a different Compose configuration and is outside the current implementation.", "ZooKeeper coordinates broker metadata; broker serves records."),
28: ("Useful commands are: docker compose up -d; docker compose ps; docker exec -it kafka-broker kafka-topics --bootstrap-server localhost:9092 --list; --describe --topic task-queue; kafka-console-consumer --topic task-queue --from-beginning; docker compose down. Use the container's CLI so versions match.", "Start -> inspect -> create/describe -> produce/consume -> stop."),
29: ("Test path: start Compose, run consumer.py, run producer.py, open localhost:5001, submit a task, watch QUEUED become PROCESSING and COMPLETED, then call GET /tasks. The CLI also supports POST /submit-task and GET /health.", "Infrastructure -> worker -> API -> event -> result -> dashboard."),
30: ("For connection errors, check Docker and 9092. For no messages, check topic, group, offsets, and whether another consumer already owns the partition. Duplicate messages can follow a crash before auto-commit. Ordering is only per partition. Topic existence can be checked with kafka-topics --describe.", "Observe logs first; verify broker, topic, group, partition, and files."),
31: ("Lag is produced records minus consumed progress. The code does not expose a lag metric, but Kafka CLI or monitoring tools can measure it. Lag grows when task processing is slower than production, especially because the simulated worker handles one message at a time.", "More input than processing capacity -> backlog -> lag."),
32: ("The beginner stage is Flask -> one Kafka topic -> one worker. An intermediate system adds APIs, multiple consumer groups, and a database. Production adds multiple brokers, replication, observability, schema governance, security, and separate topics for business events.", "Scale by separating request handling, transport, workers, and storage."),
33: ("Examples map directly to the same pattern: orders producer -> orders topic -> fulfillment consumer; payment event -> payment topic -> notification consumer; logs -> log topic -> analytics consumer. The current project specifically represents background task execution.", "Event producer -> named topic -> specialized consumer group."),
34: ("Throughput growth requires more partitions, consumers, brokers, and storage. A group can parallelize only up to the number of partitions. This project has one worker loop and no throughput or lag monitoring, so it is a learning-scale system.", "Increase partitions -> add group members -> distribute work -> monitor lag."),
35: ("Replication is not meaningfully implemented here: one broker and replication factors of 1 are configured. In production, a partition has a leader and followers; ISR members replicate it, and a healthy follower can become leader after failure.", "Leader accepts writes -> followers replicate -> failover if leader fails."),
36: ("Kafka does not delete a record when this consumer reads it. Retention is broker policy. This Compose file does not set application retention values. Retention makes replay possible, unlike a simple destructive queue.", "Write -> retain by time/size -> consumer reads -> record remains until retention removes it."),
37: ("Kafka favors durable logs, replay, partitions, and high throughput. RabbitMQ-style queues often emphasize routing and work-queue delivery. Choose Kafka for streams and replay; choose a traditional queue for simpler command delivery when replay and partition scaling are not central.", "Compare ordering, replay, retention, consumer groups, and throughput."),
38: ("No authentication, authorization, TLS, SASL, or secret manager is configured. The broker uses PLAINTEXT. Environment variables only override the bootstrap address. Production should protect credentials, encrypt traffic, restrict ACLs, and avoid secrets in source files.", "Current: trusted local network. Production: identity + encryption + ACLs."),
39: ("The code logs connections, sends, partitions, offsets, and task results, but it does not expose broker health, consumer lag, throughput, disk, or under-replicated partition metrics. Recommended tools include Kafka UI, JMX exporters, Prometheus, and Grafana.", "Instrument producer, broker, consumer, and business outcomes."),
40: ("Good next steps are stable topic names, deliberate partition counts, keys for ordering, bounded message sizes, retries, dead-letter topics, idempotent handlers, schema validation, and lag monitoring. In this project, start with atomic result writes and a real durable database.", "Design topic -> choose key/partitions -> validate -> process safely -> observe."),
41: ("Implemented API routes are GET /, POST /submit-task, GET /tasks, and GET /health on port 5001. POST accepts JSON or form data. It creates the event and returns 201; the consumer does not respond synchronously to the original POST.", "Client -> Flask -> Kafka -> worker -> files -> GET /tasks."),
42: ("There is no database. submitted_tasks.json and task_results.json are local files, and queue_buffer.json is a fallback queue. This is useful for learning but unsafe for multiple processes, crashes during writes, and horizontal scaling.", "Consumer -> atomic JSON result file -> producer merges -> dashboard."),
43: ("A faithful architecture is: browser/API -> Flask producer -> JSON serializer -> Kafka broker -> task-queue -> partition -> task-processor-group -> consumer.py -> task_results.json -> Flask sync -> dashboard. The fallback branch writes queue_buffer.json when Kafka send fails.", "Normal path and fallback path are both explicit in the code."),
44: ("Sequence: client POSTs; Flask validates and creates payload; producer sends; broker assigns metadata; consumer fetches; worker marks PROCESSING; worker sleeps through three stages; worker writes COMPLETED; dashboard polls GET /tasks. The original POST does not wait for completion.", "POST -> send -> fetch -> process -> persist -> poll."),
45: ("The repository is small: producer.py, consumer.py, docker-compose.yml, requirements.txt, templates/dashboard.html, and JSON state files. __pycache__ is generated runtime output. README.md is existing project guidance.", "Infrastructure + producer + consumer + UI + local state."),
46: ("producer.py owns HTTP and publishing; consumer.py owns polling and work; docker-compose.yml owns Kafka infrastructure; dashboard.html owns browser rendering and five-second polling; requirements.txt owns Python dependencies; JSON files hold demo state.", "Entry point -> imported library -> Kafka/file side effect -> next component."),
47: ("Core terms: broker is a Kafka server; topic is a named log; partition is an ordered lane; offset is a position; producer writes; consumer reads; group shares work; retention controls lifetime; lag is unprocessed distance; serialization converts objects to bytes; rebalancing redistributes partitions.", "Use the glossary to translate Kafka words into project actions."),
48: ("Beginner interview answers should be project-specific: Kafka decouples Flask from slow work; task-queue is the topic; task-processor-group shares partitions; offsets track progress; JSON is the wire format; auto-commit means duplicates are possible; one broker is a single point of failure.", "Answer what this code does before describing ideal Kafka behavior."),
49: ("Two-minute answer: This project is a Flask task queue. A user submits a task; producer.py validates it, assigns an ID, serializes JSON, and sends it to task-queue. consumer.py, in task-processor-group, reads it, simulates priority-based work, and writes status to task_results.json. The dashboard polls Flask to show progress. It is a learning system, not a production cluster.", "Keep the interview story: problem -> producer -> Kafka -> consumer -> outcome."),
50: ("Five-minute answer should add broker localhost:9092, one topic, group_id, partition/offset metadata, earliest reset, automatic commits, status transitions, JSON serializer/deserializer, retries, fallback buffer, and the limitations of local files and one broker.", "Expand the two-minute story with one message's technical lifecycle."),
51: ("Kafka is not the database or API. A topic is not a table; a partition is not a topic; a group is not one consumer; reading does not immediately delete a record; two different groups can read the same record; duplicates are possible; offsets enable restart and replay.", "If confused, return to: durable log + partitions + consumer progress."),
52: ("The requested split is represented by docs/topics/01-...md through 60-...md, plus a master document. Each topic file is beginner-oriented and names the actual project files and workflow.", "Open a topic file for focused learning; use the master for the complete path."),
53: ("The master file combines all 60 sections, the project facts, diagrams, commands, workflows, limitations, and final report. It is the easiest file to search and share as source Markdown.", "Topic pages -> ordered master Markdown -> PDF rendering."),
54: ("The PDF is a formatted study guide with title page, contents, project facts, and one topic section per numbered requirement. It includes readable workflows, code references, commands, and production notes.", "Markdown content -> ReportLab styles -> page breaks -> validated PDF."),
55: ("Quality checks include generated page count, extractable text, section presence, output file existence, and PNG rendering of representative pages. Visual inspection should confirm headings, wrapping, footer numbers, and diagrams are readable.", "Generate -> render -> inspect -> fix -> deliver."),
56: ("The master flow is: user/application -> Flask producer -> JSON serialization -> broker -> task-queue -> partition/offset -> consumer group -> consumer -> JSON deserialization -> processing -> result file -> dashboard. The configured system has one broker and one normal worker.", "This is the complete mental model for the repository."),
57: ("Remember: a user submits a task to Flask. Flask puts a JSON event into Kafka. Kafka stores it in a topic partition with an offset. The consumer reads it, performs work, and records the result. The dashboard learns the result by polling Flask. Kafka makes the slow work asynchronous.", "Short memory aid: submit -> store -> read -> work -> record -> display."),
58: ("Project: Apache Kafka Task Queue System. Language: Python. Library: Flask, kafka-python, Jinja2, colorama. Broker: localhost:9092, one Docker broker. Topic: task-queue. Group: task-processor-group. Producer: producer.py. Consumer: consumer.py. State: JSON files. API: four Flask routes. Missing: database, replication, security, schema registry, metrics, dead-letter topic, and true exactly-once processing.", "Recommended improvements: durable storage, multiple brokers, explicit partitions, secure listeners, monitoring, retries, idempotency, tests, and CI."),
59: ("The deliverable set contains 60 topic Markdown files and one master Markdown file. The PDF is a single complete document so it can be printed or shared. Each topic is kept in the same order as the pasted requirements.", "Use individual files for focused study and the PDF for a linear course."),
60: ("For every message ask five questions: What data was created? Which file sent it? Where is it stored? Which consumer processed it? What state was persisted afterward? In this repository the answer is a task dictionary, producer.py, task-queue partition/offset, consumer.py, and task_results.json/submitted_tasks.json.", "Created -> serialized -> broker -> partition/offset -> fetched -> deserialized -> processed -> persisted -> displayed."),
}

# The pasted prompt skips the number 22. Fill that numbering gap with the
# configuration topic, then shift the later topic facts by one position.
custom = {(k if k < 22 else k + 1): v for k, v in custom.items()}
custom[22] = ("Configuration is read mostly from code and environment. producer.py and consumer.py use KAFKA_BOOTSTRAP_SERVERS, defaulting to localhost:9092. The topic and group are constants. Docker Compose defines ports, listeners, ZooKeeper, auto topic creation, and single-replica internal settings.", "Environment/defaults -> Kafka client configuration -> broker connection -> topic/group behavior.")

def md_for(i, title, body, flow):
    return f"# {i}. {title}\n\n{project_facts}\n\n## Beginner meaning\n\n{body}\n\n## Workflow\n\n```text\n{flow}\n```\n\n## What is implemented\n\nThe statements above describe the current repository. Features labelled as recommendations are not currently implemented. Check the source files before changing behavior.\n"

def write_docs():
    files = []
    for i, title in enumerate(titles, 1):
        body, flow = custom[i]
        safe = title.lower().replace(':', '').replace('/', '-').replace('?', '').replace(' ', '-')
        name = f"{i:02d}-{safe}.md"
        path = TOPICS_DIR / name
        path.write_text(md_for(i, title, body, flow), encoding="utf-8")
        files.append(path)
    master = ["# Complete Kafka Documentation - Beginner to Project to Production", "", project_facts, "", "## Contents", ""]
    master += [f"{i}. [{title}](topics/{files[i-1].name})" for i, title in enumerate(titles, 1)]
    master += ["", "## Project truth", "", "This documentation is based on the files present in this repository. When a feature is absent, it is marked as not implemented rather than assumed.", ""]
    for i, title in enumerate(titles, 1):
        body, flow = custom[i]
        master += [f"## {i}. {title}", "", body, "", "### Workflow", "", "```text", flow, "```", ""]
    master += ["## Final project report", "", "- Project: Apache Kafka Task Queue System", "- Language: Python", "- Kafka library: kafka-python", "- Kafka version/image: Confluent Platform 7.5.0 container", "- Broker: localhost:9092; one broker", "- Topics: task-queue", "- Consumer group: task-processor-group", "- Producer: producer.py", "- Consumer: consumer.py", "- API: /, /submit-task, /tasks, /health", "- State files: submitted_tasks.json, task_results.json, queue_buffer.json", "- Not implemented: database, replication beyond factor 1, security, schema registry, metrics, dead-letter topic, exactly-once processing.", ""]
    master_path = DOCS / "COMPLETE_KAFKA_DOCUMENTATION.md"
    master_path.write_text("\n".join(master), encoding="utf-8")
    return files, master_path

def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawString(0.65 * inch, 0.42 * inch, "Kafka Task Queue Documentation")
    canvas.drawRightString(7.85 * inch, 0.42 * inch, f"Page {doc.page}")
    canvas.restoreState()

def build_pdf(files):
    out = PDF_DIR / "COMPLETE_KAFKA_DOCUMENTATION.pdf"
    doc = SimpleDocTemplate(str(out), pagesize=letter, rightMargin=0.62*inch, leftMargin=0.62*inch, topMargin=0.62*inch, bottomMargin=0.65*inch)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Cover", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=25, leading=31, alignment=TA_CENTER, textColor=colors.HexColor("#0B3954"), spaceAfter=20))
    styles.add(ParagraphStyle(name="Sub", parent=styles["Normal"], fontSize=11, leading=16, alignment=TA_CENTER, textColor=colors.HexColor("#444444")))
    styles.add(ParagraphStyle(name="Topic", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=17, leading=21, textColor=colors.HexColor("#0B3954"), spaceAfter=10))
    styles.add(ParagraphStyle(name="H2x", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=colors.HexColor("#136F8A"), spaceBefore=8, spaceAfter=4))
    styles.add(ParagraphStyle(name="Bodyx", parent=styles["BodyText"], fontSize=9.2, leading=12.6, spaceAfter=6))
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8, leading=10.5, textColor=colors.HexColor("#555555")))
    story = [Paragraph("Apache Kafka Task Queue System", styles["Cover"]), Paragraph("Complete beginner documentation based on the actual repository", styles["Sub"]), Spacer(1, 0.3*inch), Paragraph("60 numbered topics: understanding words, exact project behavior, and workflows", styles["Sub"]), Spacer(1, 2.3*inch), Paragraph("Project facts", styles["H2x"]), Paragraph(project_facts, styles["Bodyx"]), PageBreak()]
    story += [Paragraph("Contents", styles["Topic"])]
    table_data = [["No.", "Topic"]] + [[str(i), title] for i, title in enumerate(titles, 1)]
    table = Table(table_data, colWidths=[0.45*inch, 6.75*inch], repeatRows=1)
    table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0B3954")), ("TEXTCOLOR", (0,0), (-1,0), colors.white), ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"), ("FONTSIZE", (0,0), (-1,-1), 7.5), ("LEADING", (0,0), (-1,-1), 9), ("GRID", (0,0), (-1,-1), 0.25, colors.HexColor("#CCCCCC")), ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F1F6F8")]), ("VALIGN", (0,0), (-1,-1), "TOP"), ("LEFTPADDING", (0,0), (-1,-1), 5), ("RIGHTPADDING", (0,0), (-1,-1), 5)]))
    story += [table]
    for i, title in enumerate(titles, 1):
        body, flow = custom[i]
        flow_html = escape(flow).replace(" -> ", " -&gt;<br/>")
        story += [PageBreak(), Paragraph(f"{i}. {title}", styles["Topic"]), Paragraph(project_facts, styles["Small"]), Paragraph("Beginner meaning", styles["H2x"]), Paragraph(body, styles["Bodyx"]), Paragraph("Workflow", styles["H2x"]), Paragraph(flow_html, styles["Small"]), Paragraph("Implementation note", styles["H2x"]), Paragraph("This page describes what the current repository implements. Any production improvement mentioned is a recommendation, not an existing feature.", styles["Bodyx"])]
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return out

if __name__ == "__main__":
    files, master = write_docs()
    pdf = build_pdf(files)
    print(f"Created {len(files)} topic Markdown files")
    print(master)
    print(pdf)

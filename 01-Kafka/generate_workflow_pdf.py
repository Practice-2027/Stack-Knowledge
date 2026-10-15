from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Flowable, KeepTogether

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output" / "pdf" / "KAFKA_WORKFLOW_DEEP_DIVE.pdf"
OUT.parent.mkdir(parents=True, exist_ok=True)

BLUE = colors.HexColor("#0B3954")
TEAL = colors.HexColor("#136F8A")
LIGHT = colors.HexColor("#EAF4F7")
ORANGE = colors.HexColor("#D97706")
GREEN = colors.HexColor("#15803D")
RED = colors.HexColor("#B91C1C")

class WorkflowDiagram(Flowable):
    def __init__(self, title, boxes, width=7.1*inch, box_h=0.48*inch, gap=0.22*inch, fill=LIGHT):
        Flowable.__init__(self)
        self.title = title
        self.boxes = boxes
        self.width = width
        self.box_h = box_h
        self.gap = gap
        self.fill = fill
        self.height = 0.32*inch + box_h + 0.38*inch

    def draw(self):
        c = self.canv
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(BLUE)
        c.drawString(0, self.height - 11, self.title)
        n = len(self.boxes)
        bw = (self.width - self.gap*(n-1)) / n
        y = 0.25*inch
        for i, label in enumerate(self.boxes):
            x = i*(bw+self.gap)
            c.setFillColor(self.fill)
            c.setStrokeColor(TEAL)
            c.roundRect(x, y, bw, self.box_h, 5, fill=1, stroke=1)
            c.setFillColor(colors.black)
            c.setFont("Helvetica", 7.4)
            words = label.split()
            lines, line = [], ""
            for word in words:
                test = (line + " " + word).strip()
                if c.stringWidth(test, "Helvetica", 7.4) > bw-10 and line:
                    lines.append(line); line = word
                else:
                    line = test
            if line: lines.append(line)
            start = y + self.box_h/2 + (len(lines)-1)*4
            for j, text in enumerate(lines[:3]):
                c.drawCentredString(x+bw/2, start-j*9, text)
            if i < n-1:
                c.setStrokeColor(ORANGE)
                c.setFillColor(ORANGE)
                ax = x+bw+2; ay = y+self.box_h/2
                c.line(ax, ay, ax+self.gap-6, ay)
                c.line(ax+self.gap-6, ay, ax+self.gap-11, ay+3)
                c.line(ax+self.gap-6, ay, ax+self.gap-11, ay-3)

class VerticalFlow(Flowable):
    def __init__(self, title, steps, width=7.1*inch, box_h=0.4*inch):
        Flowable.__init__(self)
        self.title, self.steps, self.width, self.box_h = title, steps, width, box_h
        self.height = 0.28*inch + len(steps)*0.58*inch

    def draw(self):
        c = self.canv
        c.setFont("Helvetica-Bold", 9); c.setFillColor(BLUE); c.drawString(0, self.height-10, self.title)
        y = self.height - 0.55*inch
        x = 0.18*inch; w = self.width-0.36*inch
        for i, step in enumerate(self.steps):
            c.setFillColor(LIGHT if i % 2 == 0 else colors.white); c.setStrokeColor(TEAL)
            c.roundRect(x, y, w, self.box_h, 5, fill=1, stroke=1)
            c.setFillColor(colors.black); c.setFont("Helvetica", 8)
            c.drawString(x+8, y+self.box_h/2-3, step)
            if i < len(self.steps)-1:
                c.setStrokeColor(ORANGE); c.setFillColor(ORANGE)
                c.line(x+w/2, y-2, x+w/2, y-0.16*inch)
                c.line(x+w/2, y-0.16*inch, x+w/2-3, y-0.16*inch+5)
                c.line(x+w/2, y-0.16*inch, x+w/2+3, y-0.16*inch+5)
            y -= 0.58*inch

def footer(canvas, doc):
    canvas.saveState(); canvas.setFont("Helvetica", 8); canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawString(0.65*inch, 0.42*inch, "Kafka Workflow Deep Dive")
    canvas.drawRightString(7.85*inch, 0.42*inch, f"Page {doc.page}"); canvas.restoreState()

def p(text, style): return Paragraph(text, style)

def build():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Cover", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=25, leading=30, alignment=TA_CENTER, textColor=BLUE, spaceAfter=16))
    styles.add(ParagraphStyle(name="Sub", parent=styles["Normal"], fontSize=11, leading=16, alignment=TA_CENTER, textColor=colors.HexColor("#444444")))
    styles.add(ParagraphStyle(name="H1x", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=BLUE, spaceAfter=9))
    styles.add(ParagraphStyle(name="H2x", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=TEAL, spaceBefore=8, spaceAfter=4))
    styles.add(ParagraphStyle(name="Bodyx", parent=styles["BodyText"], fontSize=9.2, leading=13, spaceAfter=6))
    styles.add(ParagraphStyle(name="Smallx", parent=styles["BodyText"], fontSize=8, leading=10.5, textColor=colors.HexColor("#555555")))
    styles.add(ParagraphStyle(name="Callout", parent=styles["BodyText"], fontSize=9, leading=12, leftIndent=8, rightIndent=8, borderColor=ORANGE, borderWidth=1, borderPadding=6, backColor=colors.HexColor("#FFF8EB"), spaceBefore=5, spaceAfter=8))

    story = [p("Kafka Task Queue System", styles["Cover"]), p("Deep workflow explanation with diagrams", styles["Sub"]), Spacer(1, 0.25*inch), p("Based on producer.py, consumer.py, docker-compose.yml, and dashboard.html", styles["Sub"]), Spacer(1, 1.6*inch), p("The one-message question", styles["H2x"]), p("What exactly happens after a user submits one task? This guide follows that task through HTTP, Flask, JSON serialization, Kafka topic and partition, offset, consumer group, worker processing, result persistence, and dashboard refresh.", styles["Bodyx"]), p("Actual configuration: topic task-queue, broker localhost:9092, group task-processor-group, ZooKeeper on 2181, one Docker broker, JSON values, and local JSON files for state.", styles["Callout"]), PageBreak()]

    story += [p("1. System at a glance", styles["H1x"]), p("The application has two long-running Python processes. producer.py is both the Flask web server and Kafka producer. consumer.py is the worker and Kafka consumer. They do not call each other directly; Kafka is the transport between them.", styles["Bodyx"]), WorkflowDiagram("Normal message path", ["Browser or API", "Flask producer", "JSON serializer", "Kafka broker", "task-queue", "Consumer worker", "Result files", "Dashboard"]), Spacer(1, 0.12*inch), p("The browser only waits for the enqueue response. The slow work happens later in the consumer. That separation is the reason the dashboard can remain responsive while a task takes 2, 3.5, or 5 seconds.", styles["Bodyx"]), PageBreak()]

    story += [p("2. Startup workflow", styles["H1x"]), p("Docker must provide Kafka before the Python clients can use it. The Compose file starts ZooKeeper first, then the Kafka broker. The producer and consumer both tolerate a broker that is still booting, but their retry behavior is different.", styles["Bodyx"]), VerticalFlow("Startup sequence", ["docker compose up -d", "ZooKeeper listens on 2181", "Kafka broker listens on 9092", "consumer.py creates KafkaConsumer", "producer.py creates KafkaProducer", "Flask serves port 5001"]), p("consumer.py tries twice and falls back to standalone queue mode if Kafka is unavailable. producer.py tries to connect during startup and also retries when a request needs a producer. The system can therefore start in a degraded local-file mode, but that mode is not Kafka processing.", styles["Bodyx"]), PageBreak()]

    story += [p("3. One task: HTTP to Kafka", styles["H1x"]), p("A task begins at POST /submit-task. The route accepts JSON or form fields. It requires task_name and normalizes priority to HIGH, MEDIUM, or LOW. Invalid priority values become MEDIUM.", styles["Bodyx"]), WorkflowDiagram("Submission workflow", ["POST /submit-task", "Validate fields", "Create task ID", "Build payload", "producer.send()", "flush + future.get()", "Return 201"]), p("The generated payload contains task_id, task_name, priority, status=QUEUED, submitted_at, and empty completion fields. The value serializer converts the dictionary into JSON UTF-8 bytes. Because no key is passed to send(), the application does not control partition selection with a business key.", styles["Bodyx"]), p("Important timing: the route waits for Kafka metadata for up to the configured timeouts, but it does not wait for the consumer to finish the task.", styles["Callout"]), PageBreak()]

    story += [p("4. What Kafka does with the record", styles["H1x"]), p("After producer.send(), the Kafka client sends a record to the broker. Kafka appends it to a partition log. The record receives a partition number and an offset. Those two values identify its position in the topic log.", styles["Bodyx"]), WorkflowDiagram("Broker-side workflow", ["Producer bytes", "Broker receives", "Partition chosen", "Offset assigned", "Record appended", "Metadata returned"]), p("The producer prints the topic, partition, and offset from future.get(). The offset is not the task ID. The task ID is part of the JSON value and is used by the application to match status updates. The offset is Kafka's position marker and is used by the consumer group to track progress.", styles["Bodyx"]), PageBreak()]

    story += [p("5. Consumer group and polling", styles["H1x"]), p("consumer.py creates KafkaConsumer for task-queue with group_id=task-processor-group. The consumer joins the group and receives ownership of the available partition. The for message in consumer loop repeatedly fetches records from Kafka.", styles["Bodyx"]), WorkflowDiagram("Read workflow", ["Consumer joins group", "Partition assigned", "Fetch request", "Broker returns record", "message.value", "process_task()"]), p("The consumer is pull-based. Kafka does not invoke a Python callback for every message. The client asks Kafka for data, which lets the worker control how quickly it reads and processes work. With one partition, adding more workers to the same group cannot create more than one active owner for that partition.", styles["Bodyx"]), PageBreak()]

    story += [p("6. Inside process_task()", styles["H1x"]), p("The worker deserializes JSON into a Python dictionary before process_task() runs. It reads task_id, task_name, priority, and submitted_at. Priority selects a simulated duration: HIGH 2.0 seconds, MEDIUM 3.5 seconds, LOW 5.0 seconds.", styles["Bodyx"]), VerticalFlow("Worker processing workflow", ["Receive message and print partition/offset", "Write PROCESSING to task_results.json", "Allocate resources and parse parameters", "Execute simulated business logic", "Validate output and persist state", "Write COMPLETED with duration"]), p("The three sleeps represent stages of real work. They are only a simulation; this project does not call an external business service. The result file is updated atomically by writing a temporary file and replacing the original.", styles["Bodyx"]), PageBreak()]

    story += [p("7. How status returns to the dashboard", styles["H1x"]), p("Kafka carries the task event, but the dashboard does not read Kafka directly. consumer.py writes status into task_results.json. When Flask handles GET / or GET /tasks, producer.py reads that result file and merges matching records into submitted_tasks.json.", styles["Bodyx"]), WorkflowDiagram("Status synchronization", ["Worker writes result", "task_results.json", "GET /tasks", "sync_tasks_with_results()", "submitted_tasks.json", "Browser renders status"]), p("The browser polls GET /tasks every five seconds using fetch(). This produces the visible sequence QUEUED -> PROCESSING -> COMPLETED. The polling delay is a UI refresh interval, not Kafka delivery latency.", styles["Bodyx"]), PageBreak()]

    story += [p("8. Failure and fallback workflow", styles["H1x"]), p("If the producer cannot publish to Kafka, submit_task() writes the task to queue_buffer.json. The consumer checks that file and processes buffered tasks in standalone mode. This keeps the demo usable when Docker is not running, but it is a separate path with weaker durability and concurrency guarantees.", styles["Bodyx"]), WorkflowDiagram("Kafka failure branch", ["Kafka send fails", "Log warning", "Append queue_buffer.json", "Worker reads buffer", "process_task()", "Write result"], fill=colors.HexColor("#FFF8EB")), p("A Kafka send failure does not mean the event was definitely lost or definitely duplicated; the exact outcome depends on where the failure occurred. Production systems normally use explicit retry policies, idempotency keys, durable storage, and dead-letter topics rather than a shared local JSON file.", styles["Callout"]), PageBreak()]

    story += [p("9. Offset, commit, and duplicates", styles["H1x"]), p("The consumer uses enable_auto_commit=True with a one-second auto-commit interval. Processing and committing are not one atomic operation. If the worker processes a task and crashes before its offset is committed, Kafka can deliver the same record again after restart.", styles["Bodyx"]), WorkflowDiagram("Possible duplicate path", ["Fetch offset N", "Process task", "Crash before commit", "Restart consumer", "Resume earlier offset", "Process again"], fill=colors.HexColor("#FDECEC")), p("For this reason, the project most closely approaches at-least-once processing. The code does not implement exactly-once processing, a transactional producer, or an idempotent database operation. The task ID can be used as an idempotency key in a stronger design.", styles["Bodyx"]), PageBreak()]

    story += [p("10. Production workflow", styles["H1x"]), p("The learning project is intentionally small: one broker, one topic, local files, PLAINTEXT listeners, and no metrics. A production workflow adds durable databases, multiple brokers, replication, explicit partitions, secure listeners, schema governance, monitoring, retries, and dead-letter handling.", styles["Bodyx"]), WorkflowDiagram("Production evolution", ["API gateway", "Producer service", "Kafka cluster", "Multiple topics", "Consumer groups", "Database", "Metrics and alerts"]), p("The core message path does not change. What changes is the reliability around it: the broker cluster survives failure, consumers can scale across partitions, handlers can safely retry, and operators can see lag and errors before users report them.", styles["Bodyx"]), PageBreak()]

    story += [p("11. Exact answer: what happens to one message?", styles["H1x"]), p("1. A user submits task_name and priority. 2. Flask validates input and creates TASK-XXXXXXXX. 3. producer.py creates a Python dictionary. 4. kafka-python serializes it to JSON bytes. 5. Kafka appends it to task-queue. 6. Kafka assigns partition and offset. 7. task-processor-group fetches the record. 8. consumer.py deserializes JSON. 9. process_task() writes PROCESSING. 10. The worker performs three simulated stages. 11. It writes COMPLETED and duration. 12. Flask merges the result. 13. The dashboard shows the new state on its next poll.", styles["Bodyx"]), WorkflowDiagram("One-message mental model", ["Created", "Serialized", "Stored", "Positioned", "Fetched", "Processed", "Persisted", "Displayed"]), p("The most important separation is between transport state and business state. Kafka stores the event and tracks consumer progress. task_results.json stores this demo's business status. In a larger system, a database or service would own business state, while Kafka would remain the event transport.", styles["Callout"]), PageBreak()]

    story += [p("12. Debugging by workflow stage", styles["H1x"]), p("Debug in the same order as the message moves. First verify Docker and broker connectivity. Then verify the topic. Next inspect producer logs for send, partition, and offset. Then inspect consumer logs for the Kafka event and processing stages. Finally inspect task_results.json and GET /tasks.", styles["Bodyx"])]
    data = [["Stage", "Evidence to check"], ["Infrastructure", "docker compose ps; port 9092; ZooKeeper 2181"], ["Producer", "POST response; send exception; topic/partition/offset log"], ["Consumer", "group name; Kafka event; processing logs"], ["State", "task_results.json and submitted_tasks.json"], ["UI", "GET /tasks and five-second browser polling"]]
    t = Table(data, colWidths=[1.35*inch, 5.75*inch], repeatRows=1); t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), BLUE), ("TEXTCOLOR", (0,0), (-1,0), colors.white), ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"), ("FONTSIZE", (0,0), (-1,-1), 8.3), ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#C7D5DA")), ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, LIGHT]), ("VALIGN", (0,0), (-1,-1), "TOP"), ("LEFTPADDING", (0,0), (-1,-1), 6), ("RIGHTPADDING", (0,0), (-1,-1), 6)]))
    story += [t, Spacer(1, 0.16*inch), p("This stage-by-stage method prevents guessing. A task visible in submitted_tasks.json but absent from Kafka logs points to a publish or fallback issue. A Kafka event with no result points to consumer or processing failure. A completed result with an unchanged browser points to the status synchronization or UI polling layer.", styles["Bodyx"])]

    doc = SimpleDocTemplate(str(OUT), pagesize=letter, rightMargin=0.62*inch, leftMargin=0.62*inch, topMargin=0.62*inch, bottomMargin=0.65*inch)
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(OUT)

if __name__ == "__main__": build()

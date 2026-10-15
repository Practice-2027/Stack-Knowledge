"""
=============================================================================
Apache Kafka Task Queue System - Producer (Flask Web Application)
=============================================================================
This module acts as the "Producer" in our Kafka architecture.
It exposes a web dashboard and REST API to submit tasks. When a task is
received, the producer publishes a message to the 'task-queue' Kafka topic.
The background consumer will then pull and process these tasks asynchronously.

Port: 5001
Routes:
  - GET  /              : Renders the Task Dashboard UI
  - POST /submit-task   : Receives a new task, stores it, and sends it to Kafka
  - GET  /tasks         : Returns all submitted tasks and their live statuses as JSON
  - GET  /health        : Health check endpoint to verify Kafka connectivity
=============================================================================
"""

import json
import logging
import os
import time
import uuid
from datetime import datetime
from threading import Lock

from flask import Flask, jsonify, render_template, request
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable, KafkaError

# ---------------------------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [PRODUCER] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("ProducerApp")

# ---------------------------------------------------------------------------
# Application Configuration
# ---------------------------------------------------------------------------
app = Flask(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC = "task-queue"
RESULTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "task_results.json")
TASKS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "submitted_tasks.json")
BUFFER_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "queue_buffer.json")

# In-memory storage with thread safety lock
tasks_lock = Lock()
submitted_tasks = []

# Global KafkaProducer reference
producer_instance = None


# ---------------------------------------------------------------------------
# Helper: Kafka Producer Initialization & Reconnection
# ---------------------------------------------------------------------------
def get_kafka_producer(max_retries=5, retry_delay=2):
    """
    Creates and returns a KafkaProducer instance with retry logic.
    If Kafka broker is still booting, it retries up to max_retries times.
    """
    global producer_instance
    if producer_instance is not None:
        return producer_instance

    logger.info(f"Connecting to Kafka broker at '{KAFKA_BOOTSTRAP_SERVERS}'...")

    for attempt in range(1, max_retries + 1):
        try:
            producer = KafkaProducer(
                bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                # Wait up to 5 seconds for connection acknowledgment
                request_timeout_ms=5000,
                retries=3,
            )
            logger.info("Successfully connected to Apache Kafka broker!")
            producer_instance = producer
            return producer_instance
        except NoBrokersAvailable as err:
            logger.warning(
                f"[Attempt {attempt}/{max_retries}] Kafka broker not ready yet: {err}. "
                f"Retrying in {retry_delay}s..."
            )
            time.sleep(retry_delay)
        except Exception as ex:
            logger.error(f"[Attempt {attempt}/{max_retries}] Unexpected error connecting to Kafka: {ex}")
            time.sleep(retry_delay)

    logger.error("Failed to connect to Kafka broker after maximum retries.")
    return None


# ---------------------------------------------------------------------------
# Helper: Persistence & Status Synchronization
# ---------------------------------------------------------------------------
def load_persisted_tasks():
    """Load previously submitted tasks from disk on server start."""
    global submitted_tasks
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, "r", encoding="utf-8") as f:
                submitted_tasks = json.load(f)
            logger.info(f"Loaded {len(submitted_tasks)} existing tasks from '{TASKS_FILE}'.")
        except Exception as e:
            logger.warning(f"Could not load '{TASKS_FILE}': {e}")
            submitted_tasks = []


def save_persisted_tasks():
    """Save submitted tasks to disk."""
    try:
        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump(submitted_tasks, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save tasks to '{TASKS_FILE}': {e}")


def sync_tasks_with_results():
    """
    Merges status updates from consumer's 'task_results.json'
    into the in-memory and persisted task list.
    """
    global submitted_tasks
    if not os.path.exists(RESULTS_FILE):
        return

    try:
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            results_data = json.load(f)

        # Build lookup table for fast merging
        # Supports either dict keyed by task_id or list of result records
        results_map = {}
        if isinstance(results_data, dict):
            results_map = results_data
        elif isinstance(results_data, list):
            for item in results_data:
                if "task_id" in item:
                    results_map[item["task_id"]] = item

        # Update matching submitted tasks
        with tasks_lock:
            for task in submitted_tasks:
                task_id = task.get("task_id")
                if task_id in results_map:
                    res = results_map[task_id]
                    task["status"] = res.get("status", task.get("status"))
                    task["completed_at"] = res.get("completed_at")
                    task["duration_seconds"] = res.get("duration_seconds")
                    task["result_message"] = res.get("result_message")
            save_persisted_tasks()
    except Exception as e:
        logger.debug(f"Error syncing task results: {e}")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/", methods=["GET"])
def dashboard():
    """Serves the HTML task submission and monitoring dashboard."""
    sync_tasks_with_results()
    with tasks_lock:
        tasks_copy = list(submitted_tasks)
    return render_template("dashboard.html", tasks=tasks_copy)


@app.route("/tasks", methods=["GET"])
def get_tasks():
    """
    Returns the current list of all submitted tasks and their statuses.
    Used by the dashboard JavaScript auto-refresh mechanism.
    """
    sync_tasks_with_results()
    with tasks_lock:
        return jsonify({
            "status": "success",
            "total_tasks": len(submitted_tasks),
            "tasks": submitted_tasks
        }), 200


@app.route("/submit-task", methods=["POST"])
def submit_task():
    """
    Accepts task submissions via JSON or HTML form.
    Publishes the task to the Kafka 'task-queue' topic.
    """
    # Accept both JSON payload and form-encoded data
    if request.is_json:
        data = request.get_json() or {}
        task_name = data.get("task_name", "").strip()
        priority = data.get("priority", "MEDIUM").strip().upper()
    else:
        task_name = request.form.get("task_name", "").strip()
        priority = request.form.get("priority", "MEDIUM").strip().upper()

    # Input validation
    if not task_name:
        return jsonify({
            "status": "error",
            "message": "Field 'task_name' is required and cannot be empty."
        }), 400

    if priority not in ["HIGH", "MEDIUM", "LOW"]:
        priority = "MEDIUM"

    # Generate a unique task identifier and submission timestamp
    task_id = f"TASK-{uuid.uuid4().hex[:8].upper()}"
    submitted_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    task_payload = {
        "task_id": task_id,
        "task_name": task_name,
        "priority": priority,
        "status": "QUEUED",
        "submitted_at": submitted_at,
        "completed_at": None,
        "duration_seconds": None,
        "result_message": None,
    }

    # Obtain or reconnect Kafka producer
    producer = get_kafka_producer(max_retries=1, retry_delay=0)
    kafka_published = False

    if producer is not None:
        try:
            logger.info(f"Producing message to Kafka topic '{KAFKA_TOPIC}': {task_payload}")
            future = producer.send(KAFKA_TOPIC, value=task_payload)
            producer.flush(timeout=3)
            record_metadata = future.get(timeout=3)
            logger.info(
                f"Message delivered to topic '{record_metadata.topic}' "
                f"[Partition: {record_metadata.partition}, Offset: {record_metadata.offset}]"
            )
            kafka_published = True
        except Exception as ke:
            logger.warning(f"Kafka send failed: {ke}. Falling back to queue buffer.")
            kafka_published = False

    if not kafka_published:
        # Buffer fallback for standalone mode (Kafka Docker not running)
        logger.info(f"[LOCAL QUEUE] Buffering task {task_id} in queue_buffer.json for worker.")
        try:
            buf = []
            if os.path.exists(BUFFER_FILE):
                with open(BUFFER_FILE, "r", encoding="utf-8") as f:
                    buf = json.load(f)
            buf.append(task_payload)
            with open(BUFFER_FILE, "w", encoding="utf-8") as f:
                json.dump(buf, f, indent=2)
        except Exception as err:
            logger.error(f"Failed to buffer task locally: {err}")

    # Store task in local memory and file
    with tasks_lock:
        submitted_tasks.insert(0, task_payload)
        save_persisted_tasks()

    # If request came from an HTML form without AJAX, redirect to dashboard
    if not request.is_json and request.headers.get("X-Requested-With") != "XMLHttpRequest":
        from flask import redirect, url_for
        return redirect(url_for("dashboard"))

    return jsonify({
        "status": "success",
        "message": f"Task queued successfully ({'Kafka' if kafka_published else 'Standalone Queue'}).",
        "task": task_payload,
    }), 201


@app.route("/health", methods=["GET"])
def health_check():
    """Checks the health of the Flask server and Kafka connectivity."""
    producer = get_kafka_producer(max_retries=1, retry_delay=0)
    kafka_connected = producer is not None
    return jsonify({
        "status": "healthy" if kafka_connected else "degraded",
        "producer": "running",
        "kafka_connected": kafka_connected,
        "bootstrap_servers": KAFKA_BOOTSTRAP_SERVERS,
        "topic": KAFKA_TOPIC,
        "total_tasks_recorded": len(submitted_tasks),
    }), (200 if kafka_connected else 503)


# ---------------------------------------------------------------------------
# Application Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("  🚀 Apache Kafka Task Queue System - Producer Web App")
    print("=" * 65)
    print("  Dashboard URL : http://localhost:5001")
    print("  Submit API    : POST http://localhost:5001/submit-task")
    print("  Tasks API     : GET  http://localhost:5001/tasks")
    print(f"  Kafka Broker  : {KAFKA_BOOTSTRAP_SERVERS}")
    print(f"  Kafka Topic   : {KAFKA_TOPIC}")
    print("=" * 65 + "\n")

    # Load existing tasks from disk if available
    load_persisted_tasks()

    # Attempt initial connection to Kafka
    get_kafka_producer(max_retries=2, retry_delay=1)

    # Start Flask server on port 5001
    app.run(host="0.0.0.0", port=5001, debug=False)

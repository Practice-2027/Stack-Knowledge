"""
=============================================================================
Apache Kafka Task Queue System - Consumer (Worker Service)
=============================================================================
This module acts as the "Consumer" in our Kafka architecture.
It continuously listens to the 'task-queue' topic, pulls submitted tasks,
simulates real-world background processing work with realistic delays,
prints rich colored terminal logs, and records completion details in
'task_results.json' so the web dashboard can show real-time progress.

Features:
  - Auto-reconnect with retry loop if Kafka broker is booting
  - Belongs to Consumer Group 'task-processor-group'
  - Priority-based simulated execution durations
  - Cross-platform colored terminal logging (supports Colorama & ANSI)
  - Safe persistence to shared 'task_results.json'
  - Graceful shutdown on Ctrl+C (SIGINT)
=============================================================================
"""

import json
import os
import sys
import time
from datetime import datetime

from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable, KafkaError

# ---------------------------------------------------------------------------
# Cross-Platform Color Setup
# ---------------------------------------------------------------------------
try:
    import colorama
    colorama.init(autoreset=True)
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False

class Colors:
    """ANSI color escape sequences with Windows compatibility."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"

def colorize(text, color_code):
    """Applies ANSI color to text string."""
    return f"{color_code}{text}{Colors.RESET}"

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC = "task-queue"
CONSUMER_GROUP = "task-processor-group"
RESULTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "task_results.json")
BUFFER_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "queue_buffer.json")

# Simulation duration in seconds by priority
PRIORITY_DURATIONS = {
    "HIGH": 2.0,     # Fast-tracked high priority tasks
    "MEDIUM": 3.5,   # Standard priority tasks
    "LOW": 5.0,      # Background batch tasks
}


# ---------------------------------------------------------------------------
# Shared Results File Helper
# ---------------------------------------------------------------------------
def update_task_results(task_id, result_entry):
    """
    Safely reads 'task_results.json', merges the new/updated task result,
    and writes it back to disk.
    """
    results_map = {}
    if os.path.exists(RESULTS_FILE):
        try:
            with open(RESULTS_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                if isinstance(loaded, dict):
                    results_map = loaded
                elif isinstance(loaded, list):
                    for item in loaded:
                        if "task_id" in item:
                            results_map[item["task_id"]] = item
        except Exception as e:
            print(colorize(f"⚠️  [FILE WARNING] Could not read existing results: {e}", Colors.YELLOW))
            results_map = {}

    # Update or insert record
    results_map[task_id] = result_entry

    try:
        # Write to temporary file first then replace for atomic persistence
        temp_file = f"{RESULTS_FILE}.tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(results_map, f, indent=2)
        os.replace(temp_file, RESULTS_FILE)
    except Exception as e:
        print(colorize(f"❌ [FILE ERROR] Failed to write task results: {e}", Colors.RED))


# ---------------------------------------------------------------------------
# Kafka Consumer Factory with Reconnection Logic
# ---------------------------------------------------------------------------
def create_kafka_consumer():
    """
    Attempts to connect to Kafka broker. If Kafka is not ready within 2 attempts,
    returns None to gracefully switch to Standalone Queue Worker mode.
    """
    print(colorize(f"\n🔌 Probing Kafka broker at '{KAFKA_BOOTSTRAP_SERVERS}'...", Colors.CYAN))

    for attempt in range(1, 3):
        try:
            consumer = KafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
                group_id=CONSUMER_GROUP,
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                auto_commit_interval_ms=1000,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                consumer_timeout_ms=1000,
                request_timeout_ms=2000,
            )
            print(colorize(" Connected to Apache Kafka Broker successfully!", Colors.GREEN + Colors.BOLD))
            print(colorize(f" Subscribed to topic: '{KAFKA_TOPIC}' (Group: '{CONSUMER_GROUP}')\n", Colors.CYAN))
            return consumer
        except Exception:
            time.sleep(1)

    print(colorize("   [NOTE] Kafka broker not reachable on localhost:9092.", Colors.YELLOW))
    print(colorize("   [ACTIVE] Switched to STANDALONE QUEUE WORKER mode!", Colors.GREEN + Colors.BOLD))
    print(colorize(f"   Tasks will be processed directly via: {os.path.basename(BUFFER_FILE)}\n", Colors.CYAN))
    return None


# ---------------------------------------------------------------------------
# Task Processing Logic
# ---------------------------------------------------------------------------
def process_task(task_data):
    """
    Simulates work for a consumed task.
    Updates task state to 'PROCESSING', performs staged sleep,
    and records 'COMPLETED' status in 'task_results.json'.
    """
    task_id = task_data.get("task_id", "UNKNOWN-ID")
    task_name = task_data.get("task_name", "Unnamed Task")
    priority = task_data.get("priority", "MEDIUM").upper()
    submitted_at = task_data.get("submitted_at", "N/A")

    duration = PRIORITY_DURATIONS.get(priority, 3.0)
    started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    start_perf = time.time()

    # Step 1: Mark as PROCESSING in results file
    update_task_results(task_id, {
        "task_id": task_id,
        "task_name": task_name,
        "priority": priority,
        "status": "PROCESSING",
        "submitted_at": submitted_at,
        "started_at": started_at,
        "completed_at": None,
        "duration_seconds": None,
        "result_message": "Worker is currently processing task...",
    })

    # Terminal Log: Received
    print(colorize("-" * 65, Colors.DIM))
    print(
        f"{colorize('📥 [RECEIVED TASK]', Colors.CYAN + Colors.BOLD)} "
        f"{colorize(f'ID: {task_id}', Colors.WHITE + Colors.BOLD)} | "
        f"Priority: {colorize(priority, Colors.MAGENTA)} | "
        f"Time: {submitted_at}"
    )
    print(f"   Task Name : {colorize(task_name, Colors.WHITE)}")
    print(f"   Estimated : {duration:.1f} seconds workload simulation")

    # Step 2: Simulate staged work
    steps = [
        ("Step 1/3: Allocating worker resources & parsing parameters", duration * 0.3),
        ("Step 2/3: Executing business logic & heavy computation", duration * 0.4),
        ("Step 3/3: Validating output & writing persistent state", duration * 0.3),
    ]

    for step_title, step_duration in steps:
        print(f"   ⏳ {colorize(step_title, Colors.YELLOW)}...")
        time.sleep(step_duration)

    # Step 3: Compute final duration and record completion
    actual_duration = round(time.time() - start_perf, 2)
    completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result_message = f"Task completed successfully by worker in {actual_duration}s."

    update_task_results(task_id, {
        "task_id": task_id,
        "task_name": task_name,
        "priority": priority,
        "status": "COMPLETED",
        "submitted_at": submitted_at,
        "started_at": started_at,
        "completed_at": completed_at,
        "duration_seconds": actual_duration,
        "result_message": result_message,
    })

    # Terminal Log: Completed
    print(
        f"{colorize('✅ [COMPLETED TASK]', Colors.GREEN + Colors.BOLD)} "
        f"{colorize(f'ID: {task_id}', Colors.WHITE + Colors.BOLD)} in "
        f"{colorize(f'{actual_duration}s', Colors.GREEN + Colors.BOLD)}"
    )
    print(colorize("-" * 65, Colors.DIM) + "\n")


# ---------------------------------------------------------------------------
# Main Consumer Loop
# ---------------------------------------------------------------------------
def main():
    print("\n" + "=" * 65)
    print(colorize("  ⚙️  Apache Kafka Task Queue System - Consumer Worker", Colors.CYAN + Colors.BOLD))
    print("=" * 65)
    print(f"  Kafka Broker   : {KAFKA_BOOTSTRAP_SERVERS}")
    print(f"  Topic          : {KAFKA_TOPIC}")
    print(f"  Consumer Group : {CONSUMER_GROUP}")
    print(f"  Results File   : {RESULTS_FILE}")
    print("  Status         : Ready and waiting for tasks...")
    print("=" * 65)

    consumer = create_kafka_consumer()
    total_processed = 0

    try:
        while True:
            # 1. If Kafka consumer is connected, read from Kafka topic
            if consumer is not None:
                try:
                    for message in consumer:
                        task_data = message.value
                        print(
                            f"\n{colorize('📨 [KAFKA EVENT]', Colors.BLUE)} "
                            f"Partition: {message.partition} | Offset: {message.offset} | "
                            f"Timestamp: {message.timestamp}"
                        )
                        process_task(task_data)
                        total_processed += 1
                except KafkaError as ke:
                    print(colorize(f"⚠️  Kafka error: {ke}. Attempting to reconnect...", Colors.RED))
                    time.sleep(2)
                    consumer = create_kafka_consumer()

            # 2. Check local queue buffer (used when Kafka broker is offline)
            if os.path.exists(BUFFER_FILE):
                try:
                    buf = []
                    with open(BUFFER_FILE, "r", encoding="utf-8") as f:
                        buf = json.load(f)
                    if buf:
                        task_to_run = buf.pop(0)
                        with open(BUFFER_FILE, "w", encoding="utf-8") as f:
                            json.dump(buf, f, indent=2)
                        print(f"\n{colorize('📨 [STANDALONE QUEUE EVENT]', Colors.MAGENTA)} Task received from local queue buffer")
                        process_task(task_to_run)
                        total_processed += 1
                except Exception as err:
                    pass

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n" + colorize("🛑 Shutdown signal received (Ctrl+C).", Colors.YELLOW + Colors.BOLD))
    finally:
        if consumer is not None:
            print(colorize("Closing Kafka Consumer connection...", Colors.CYAN))
            try:
                consumer.close()
            except Exception:
                pass
        print(colorize(f"Worker stopped cleanly. Total tasks processed: {total_processed}", Colors.GREEN + Colors.BOLD))


if __name__ == "__main__":
    main()

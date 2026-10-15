# ⚡ Apache Kafka Task Queue System (Beginner Guide)

A complete, production-grade, beginner-friendly **Task Queue System** built with **Apache Kafka**, **Python (Flask)**, and **Docker Compose**.

This project demonstrates how real-world distributed architectures handle background workloads asynchronously: a web producer accepts long-running tasks and immediately publishes them to a Kafka topic, while an independent consumer pulls and executes the tasks in the background without blocking the user interface.

---

## 📖 Table of Contents
1. [What is Apache Kafka?](#-what-is-apache-kafka)
2. [Core Kafka Concepts Explained](#-core-kafka-concepts-explained)
3. [Architecture Diagram](#-architecture-diagram)
4. [Project Structure](#-project-structure)
5. [Prerequisites](#-prerequisites)
6. [Step-by-Step Setup Instructions](#-step-by-step-setup-instructions)
7. [Running the Application (Windows)](#-running-the-application-windows)
8. [How to Test the System](#-how-to-test-the-system)
9. [Detailed Data Flow Explanation](#-detailed-data-flow-explanation)
10. [What Each File Does](#-what-each-file-does)
11. [Troubleshooting & Common Errors](#-troubleshooting--common-errors)
12. [Next-Level Learning Exercises](#-next-level-learning-exercises)

---

## 💡 What is Apache Kafka?

**Apache Kafka** is a distributed event streaming platform designed to handle trillions of events a day. In simple terms, it acts as a **super-fast, fault-tolerant message pipeline** that allows different software applications to communicate with each other in real-time without being tightly coupled.

### The Real-World Analogy: The Airport Luggage System 🧳

Imagine a busy international airport:
- **The Check-in Counter (Producer):** You drop off your suitcase at the check-in desk. The airline staff attaches a tag, puts your bag on a conveyor belt, and immediately attends to the next passenger. They don't walk your bag to the airplane themselves!
- **The Conveyor Belts (Kafka Broker & Topics):** The conveyor network safely routes luggage into specific zones (Topics) and keeps bags in strict order.
- **The Baggage Handlers (Consumer Workers):** Teams of workers at the other end pick luggage off the belt and load it into airplanes at their own pace. If a sudden rush of 500 passengers checks in at once, the check-in counters don't crash — the conveyor belt simply buffers the luggage until handlers catch up.

Without Kafka, the check-in counter would have to personally walk each bag to the airplane and wait for confirmation before checking in the next customer — causing massive lines and system crashes!

---

## 🔑 Core Kafka Concepts Explained

| Concept | What It Is | Real-World Analogy |
| :--- | :--- | :--- |
| **Broker** | A Kafka server that receives, stores, and serves messages. A cluster is made of one or more brokers. | The airport terminal building. |
| **Topic** | A named category or feed to which messages are published (e.g., `task-queue`). | A labeled conveyor belt (e.g., "Flight 402 Luggage"). |
| **Partition** | A topic is split into partitions for parallelism and high throughput. Messages in a partition are strictly ordered. | Multiple lanes on the same conveyor belt. |
| **Offset** | A sequential integer assigned to each message in a partition, indicating its position. | A numbered ticket or bookmark. |
| **Producer** | An application that creates and sends messages to a Kafka topic (our Flask web API). | The check-in attendant putting bags on the belt. |
| **Consumer** | An application that reads and processes messages from a topic (our `consumer.py` worker). | The baggage handler picking bags off the belt. |
| **Consumer Group** | A collection of consumers working together to share the load of a topic. | A team of workers sharing the bags from the belt. |
| **ZooKeeper** | A distributed coordination service that tracks the status of Kafka brokers and metadata. | The airport control tower coordinating runway traffic. |

---

## 📐 Architecture Diagram

```
+-----------------------------------------------------------------------------------+
|                                 USER / CLIENT                                     |
|    - Web Browser (http://localhost:5001)                                          |
|    - REST API Client (curl / Postman / PowerShell)                                |
+-----------------------------------------------------------------------------------+
                                         |
                                         | 1. POST /submit-task
                                         v
+-----------------------------------------------------------------------------------+
|                        PRODUCER SERVICE (Flask Web App)                           |
|  - File: producer.py                                                              |
|  - Port: 5001                                                                     |
|  - Generates Task ID: TASK-A1B2C3D4                                               |
|  - Records task in submitted_tasks.json                                           |
|  - Publishes task JSON payload to Kafka Topic                                     |
+-----------------------------------------------------------------------------------+
                                         |
                                         | 2. KafkaProducer.send('task-queue')
                                         v
+-----------------------------------------------------------------------------------+
|                        APACHE KAFKA CLUSTER (Docker)                              |
|                                                                                   |
|   +-----------------------+              +------------------------------------+   |
|   |   Zookeeper (2181)    |<------------>|       Kafka Broker (9092)          |   |
|   | Cluster Coordination  |              | Topic: 'task-queue'                |   |
|   +-----------------------+              | [Partition 0]: [Msg1][Msg2][Msg3]  |   |
|                                          +------------------------------------+   |
+-----------------------------------------------------------------------------------+
                                         |
                                         | 3. KafkaConsumer.poll() / stream
                                         v
+-----------------------------------------------------------------------------------+
|                         CONSUMER WORKER (Python Service)                          |
|  - File: consumer.py                                                              |
|  - Group: 'task-processor-group'                                                  |
|  - Reads task payload from 'task-queue'                                           |
|  - Simulates work (time.sleep based on HIGH / MEDIUM / LOW priority)              |
|  - Emits colored terminal logs                                                    |
|  - Writes completed status into task_results.json                                 |
+-----------------------------------------------------------------------------------+
                                         |
                                         | 4. Sync State / Poll Updates
                                         v
+-----------------------------------------------------------------------------------+
|                         WEB DASHBOARD (templates/dashboard.html)                  |
|  - Auto-refreshes every 5s via GET /tasks                                         |
|  - Displays live task state: QUEUED -> PROCESSING -> COMPLETED                    |
+-----------------------------------------------------------------------------------+
```

---

## 📂 Project Structure

```
01-Kafka/
├── docker-compose.yml        # Multi-container setup for Kafka Broker and ZooKeeper
├── requirements.txt          # Python library dependencies (flask, kafka-python, etc.)
├── producer.py               # Flask web server (Producer) & task management API
├── consumer.py               # Background worker (Consumer) processing tasks from Kafka
├── submitted_tasks.json      # (Auto-generated) Persistence for submitted tasks
├── task_results.json         # (Auto-generated) Shared completion results from consumer
├── templates/
│   └── dashboard.html        # Clean, self-contained HTML/CSS/JS dashboard UI
└── README.md                 # Complete documentation and setup manual
```

---

## 💻 Prerequisites

Ensure you have the following installed on your machine:
1. **Docker & Docker Compose** (e.g., [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/))
   - *Ensure Docker Desktop is started and the engine is running.*
2. **Python 3.8 or higher** (Python 3.10, 3.11, or 3.12/3.13)
   - Verify by running:
     ```powershell
     python --version
     ```

---

## 🚀 Step-by-Step Setup Instructions

### Step 1: Open Terminal in Project Directory
Open **PowerShell** or **Command Prompt** and navigate to this folder:
```powershell
cd "c:\Users\itzme\Desktop\All Stacks\01-Kafka"
```

### Step 2: Start Kafka and ZooKeeper
Spin up the Kafka cluster in the background using Docker Compose:
```powershell
docker compose up -d
```
> **Tip:** First-time launch downloads the official Confluent Docker images (~500MB). Wait about 15–20 seconds for the Kafka broker to initialize.

To check if both containers are healthy:
```powershell
docker compose ps
```
You should see `kafka-broker` (port 9092) and `kafka-zookeeper` (port 2181) with status `Up`.

---

### Step 3: Set Up Python Virtual Environment & Install Dependencies

It is best practice to install dependencies inside a dedicated virtual environment:

#### On Windows (PowerShell):
```powershell
# Create virtual environment named 'venv'
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt
```

> **Note for Python 3.12+ users:** If `pip install kafka-python` throws an error regarding `imp`, install the actively maintained drop-in fork:
> ```powershell
> pip install kafka-python-ng flask jinja2 colorama
> ```

---

## 🏃 Running the Application (Windows)

To experience the real-time producer-consumer decoupled workflow, open **two separate terminal windows**.

### Terminal 1: Run the Consumer Worker
In your first PowerShell terminal (with `venv` activated):
```powershell
cd "c:\Users\itzme\Desktop\All Stacks\01-Kafka"
.\venv\Scripts\Activate.ps1
python consumer.py
```
**What you will see:**
```
=================================================================
  ⚙️  Apache Kafka Task Queue System - Consumer Worker
=================================================================
  Kafka Broker   : localhost:9092
  Topic          : task-queue
  Consumer Group : task-processor-group
  Results File   : ...\task_results.json
  Status         : Ready and waiting for tasks...
=================================================================
 Connected to Apache Kafka Broker successfully!
 Subscribed to topic: 'task-queue' (Group: 'task-processor-group')
```
*Leave this terminal running. It is continuously listening for tasks.*

---

### Terminal 2: Run the Flask Web Producer
In a second PowerShell terminal:
```powershell
cd "c:\Users\itzme\Desktop\All Stacks\01-Kafka"
.\venv\Scripts\Activate.ps1
python producer.py
```
**What you will see:**
```
=================================================================
  🚀 Apache Kafka Task Queue System - Producer Web App
=================================================================
  Dashboard URL : http://localhost:5001
  Submit API    : POST http://localhost:5001/submit-task
  Tasks API     : GET  http://localhost:5001/tasks
  Kafka Broker  : localhost:9092
  Kafka Topic   : task-queue
=================================================================
 * Serving Flask app 'producer'
 * Running on http://127.0.0.1:5001
```

---

## 🧪 How to Test the System

### Test Option 1: Using the Web Dashboard (Recommended)
1. Open your web browser and navigate to:
   ```
   http://localhost:5001
   ```
2. Type a task name (e.g., `Process User Video Upload`) or click one of the **Quick Samples** buttons.
3. Select a priority (`HIGH`, `MEDIUM`, or `LOW`).
4. Click **Enqueue Task**.
5. **Watch what happens:**
   - The task immediately appears in the table as **`QUEUED`**.
   - In **Terminal 1 (Consumer)**, you will see colored log outputs as it receives the task and steps through the simulation.
   - The status on the dashboard updates to **`PROCESSING`**, and within a few seconds updates to **`COMPLETED`**!

---

### Test Option 2: Using `curl` (Command Line)
You can submit tasks directly via the REST API from any terminal:

#### High-Priority Task:
```bash
curl -X POST http://localhost:5001/submit-task \
  -H "Content-Type: application/json" \
  -d "{\"task_name\": \"Send Password Reset Email\", \"priority\": \"HIGH\"}"
```

#### Medium-Priority Task:
```bash
curl -X POST http://localhost:5001/submit-task \
  -H "Content-Type: application/json" \
  -d "{\"task_name\": \"Generate Monthly Sales Report\", \"priority\": \"MEDIUM\"}"
```

#### Low-Priority Task:
```bash
curl -X POST http://localhost:5001/submit-task \
  -H "Content-Type: application/json" \
  -d "{\"task_name\": \"Sync Data Warehouse Backup\", \"priority\": \"LOW\"}"
```

---

### Test Option 3: Using PowerShell (`Invoke-RestMethod`)
If using native Windows PowerShell without curl:
```powershell
Invoke-RestMethod -Uri "http://localhost:5001/submit-task" `
  -Method POST `
  -Headers @{ "Content-Type" = "application/json" } `
  -Body '{"task_name": "PowerShell Test Task", "priority": "HIGH"}'
```

To fetch all tasks and their live statuses via JSON:
```powershell
Invoke-RestMethod -Uri "http://localhost:5001/tasks" -Method GET
```

---

### Test Option 4: Inspecting Kafka Internals via Docker CLI
Want to see what's happening directly inside Kafka? Use Kafka's built-in command-line tools inside the Docker container:

#### 1. List all active topics:
```powershell
docker exec -it kafka-broker kafka-topics --bootstrap-server localhost:9092 --list
```
*(You will see `task-queue` in the output).*

#### 2. Describe the `task-queue` topic details:
```powershell
docker exec -it kafka-broker kafka-topics --bootstrap-server localhost:9092 --describe --topic task-queue
```

#### 3. Read messages directly off the topic from the beginning:
```powershell
docker exec -it kafka-broker kafka-console-consumer --bootstrap-server localhost:9092 --topic task-queue --from-beginning
```

---

## 🔄 Detailed Data Flow Explanation

Here is the exact lifecycle of a task from submission to completion:

```
[User Browser]
      │
      │ 1. Submits task via form or API
      ▼
[producer.py]
      │
      │ 2. Assigns UUID (e.g. TASK-9FE2B1A0) and timestamp
      │ 3. Serializes task dictionary to JSON bytes
      │ 4. Calls producer.send('task-queue', payload)
      ▼
[Kafka Broker (Topic: task-queue)]
      │
      │ 5. Writes message into Partition 0 log with unique Offset
      │ 6. Producer receives ACK with partition & offset
      ▼
[consumer.py]
      │
      │ 7. Polls Kafka broker and receives new message
      │ 8. Deserializes JSON payload
      │ 9. Marks status as 'PROCESSING' in task_results.json
      │ 10. Executes task simulation (sleep 2.0s - 5.0s based on priority)
      │ 11. Marks status as 'COMPLETED' with execution duration in task_results.json
      ▼
[dashboard.html]
      │
      │ 12. Frontend auto-refreshes every 5 seconds via GET /tasks
      │ 13. Producer merges results from task_results.json
      │ 14. Browser renders updated badges: QUEUED -> PROCESSING -> COMPLETED
```

---

## 📂 What Each File Does

### 1. `docker-compose.yml`
Defines the two core infrastructure services:
- **`zookeeper`**: Runs on port `2181`. Manages Kafka broker metadata, health checks, and cluster configuration.
- **`kafka`**: Runs on port `9092`. Configured with `confluentinc/cp-kafka:7.5.0`. Sets up listeners allowing external host scripts (`localhost:9092`) to communicate with the broker.

### 2. `requirements.txt`
Specifies all Python runtime dependencies:
- **`flask`**: Lightweight web framework for the producer API and dashboard.
- **`kafka-python`**: The official, widely used Python client for Apache Kafka.
- **`jinja2`**: Template rendering engine used by Flask.
- **`colorama`**: Cross-platform ANSI terminal coloring for the consumer worker.

### 3. `producer.py`
Acts as the **Producer** in the Kafka architecture:
- Initialized on port `5001`.
- Implements robust retry logic via `get_kafka_producer()` so it gracefully waits if Kafka is booting up.
- Exposes `POST /submit-task` to enqueue tasks.
- Exposes `GET /tasks` to return live statuses.
- Renders `templates/dashboard.html` on `GET /`.
- Persists tasks to `submitted_tasks.json` so work is preserved across restarts.

### 4. `consumer.py`
Acts as the **Consumer / Worker** in the Kafka architecture:
- Subscribes to the `task-queue` topic as part of the `task-processor-group`.
- Reconnects automatically if the broker restarts.
- Simulates realistic 3-step computational workloads (input validation, execution, state persistence).
- Prints formatted, color-coded terminal logs.
- Writes task completion records to `task_results.json`.

### 5. `templates/dashboard.html`
The interactive user interface:
- Modern dark-themed dashboard.
- Real-time queue counters (Total, Queued, Processing, Completed).
- Form with quick-sample buttons for one-click testing.
- Live data table displaying Task ID, Name, Priority, Timestamps, and Status Badges.
- Dynamic 5-second polling loop using native `fetch()` without reloading the entire page.

---

## 🛠️ Troubleshooting & Common Errors

### 1. `NoBrokersAvailable` Error
* **Cause:** The Python script tried to connect before Kafka finished starting up in Docker.
* **Solution:** Kafka takes ~15 seconds to fully initialize. `producer.py` and `consumer.py` have built-in retry loops and will automatically connect once Kafka is ready. Verify containers are running with:
  ```powershell
  docker compose ps
  ```

### 2. `docker : The term 'docker' is not recognized`
* **Cause:** Docker Desktop is either not installed or not added to your system `PATH`.
* **Solution:** Install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/). After installation, restart PowerShell or your computer.

### 3. Port Already in Use (`9092` or `5001`)
* **Cause:** Another service is using port 9092 (Kafka) or 5001 (Flask).
* **Solution:**
  - Find what is using port 5001 on Windows:
    ```powershell
    Get-Process -Id (Get-NetTCPConnection -LocalPort 5001).OwningProcess
    ```
  - Stop any existing Docker Kafka containers:
    ```powershell
    docker compose down
    ```

### 4. Python 3.12+ `ModuleNotFoundError: No module named 'imp'`
* **Cause:** Python 3.12 removed the deprecated `imp` standard library module which older versions of `kafka-python` referenced.
* **Solution:** Install the updated fork:
  ```powershell
  pip install kafka-python-ng
  ```

---

## 🎓 Next-Level Learning Exercises

Once you have the basic task queue running, here are great experiments to deepen your Kafka knowledge:

1. **Scale with Multiple Consumers:**
   Open a third terminal and run another instance of `consumer.py`. Notice how Kafka distributes tasks between the two consumers automatically within the same consumer group!
2. **Increase Partitions:**
   Re-create the `task-queue` topic with 3 partitions using `kafka-topics --alter --partitions 3`. This allows up to 3 consumer workers to process tasks simultaneously in parallel.
3. **Partition by Priority:**
   Modify `producer.py` to use `key=priority.encode('utf-8')`. This guarantees that all tasks with the same priority go to the same partition and are processed in strict FIFO order!
4. **Implement a Dead-Letter Queue (DLQ):**
   Add a failure rate simulation in `consumer.py` (e.g., `random.random() < 0.2`). If a task fails 3 times, route it to a `task-failures` topic for debugging.

---

### 🌟 Summary Checklist
- [x] Docker containers running (`docker compose up -d`)
- [x] Python dependencies installed (`pip install -r requirements.txt`)
- [x] Consumer running in Terminal 1 (`python consumer.py`)
- [x] Producer running in Terminal 2 (`python producer.py`)
- [x] Dashboard open at `http://localhost:5001`

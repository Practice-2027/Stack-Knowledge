# ⚡ 08-Injest — High-Performance Data Ingestion & ETL Pipeline Engine

> **A beginner-friendly data ingestion engine with automated 4-stage processing: Validation, Normalization, Enrichment, and Dead-Letter Queue (DLQ) Quarantine.**

---

## 1. What is Data Ingestion & ETL? (Beginner Analogy)

Imagine a city's **Water Filtration Plant**:
- Water arrives from rivers, rain, and wells in various states (muddy, containing debris, or partially clean).
- The plant doesn't dump raw river water into homes! It runs a rigorous sequence:
  1. **Screening (Validation)**: Catches large debris. If a stream contains toxic chemicals, it's immediately diverted to a **Quarantine Tank (Dead-Letter Queue)** so it doesn't contaminate the system.
  2. **Filtering (Sanitization & Normalization)**: Removes fine sediment and masks private particles (e.g., masking client IP addresses).
  3. **Mineral Treatment (Enrichment)**: Injects beneficial minerals, generates unique batch tracking IDs and verification certificates.
  4. **Reservoir Storage (Sink)**: Clean, certified water is pumped into the city reservoir ready for use.

In data architectures, **08-Injest** performs this exact job on **Port 5010**:
It accepts raw telemetry, user interactions, or batch files, filters out malformed payloads, enriches clean events, and commits them to the database.

---

## 2. Architecture & 4-Stage Pipeline

```
┌────────────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                                    │
│   • REST API Calls (POST /api/ingest/event)                            │
│   • Batch Stream Events (POST /api/ingest/batch)                       │
│   • CSV / JSON File Ingestion                                          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                       08-INJEST PIPELINE (Port 5010)                   │
│                                                                        │
│   [STAGE 1: VALIDATION]                                                │
│   Checks required fields ('event_type', 'source').                     │
│   Failed validation? ─────────────┐                                    │
│         │                         │                                    │
│         ▼                         │                                    │
│   [STAGE 2: NORMALIZATION]        │                                    │
│   ISO timestamps, whitespace,     │                                    │
│   PII masking (e.g. 192.168.x.x)  │                                    │
│         │                         │                                    │
│         ▼                         │                                    │
│   [STAGE 3: ENRICHMENT]           │                                    │
│   Generates UUID (evt_...) &      │                                    │
│   SHA256 integrity hash           │                                    │
│         │                         ▼                                    │
│         ▼             ┌───────────────────────┐                        │
│   [STAGE 4: SINK]     │ DEAD-LETTER QUEUE     │                        │
│   Commits to          │ (DLQ QUARANTINE)      │                        │
│   ingested_events     │ Records error reason  │                        │
└─────────┬─────────────┴───────────┬───────────┘                        │
          │                         │                                    │
          ▼                         ▼                                    │
┌────────────────────────────────────────────────────────────────────────┐
│                  SQLite Store: ingest_store.db                         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. What is a Dead-Letter Queue (DLQ)?

In production systems, if an event contains corrupted syntax or missing required fields:
- ❌ **Bad design**: Crash the entire server or silently discard the event.
- ✅ **Enterprise DLQ pattern**: The pipeline quarantines the bad record into the `dead_letter_queue` table along with the exact `error_reason` and receipt timestamp.
- Developers can inspect, repair, and reprocess DLQ events without data loss.

---

## 4. How to Run & Test

### Run Standalone
```powershell
cd "c:\Users\itzme\Desktop\All Stacks\08-Injest"
pip install -r requirements.txt
python app.py
```

### Access Dashboard
- Open your browser to: **`http://localhost:5010`**
- Click **"⚡ Simulate 5 Events"** to immediately test the pipeline!
  - 4 valid events will pass through all 4 stages into **Clean Ingested Events**.
  - 1 deliberately malformed event will be diverted to the **Dead-Letter Queue (DLQ)**.

### Test via Terminal (PowerShell or cURL)

#### 1. Ingest a Single Clean Event
```powershell
curl -X POST http://localhost:5010/api/ingest/event `
     -H "Content-Type: application/json" `
     -d '{"event_type": "user_checkout", "source": "web_store", "payload": {"item": "Laptop", "amount": 999.0, "ip": "192.168.1.45"}}'
```

#### 2. Send a Malformed Event to Test the DLQ
```powershell
curl -X POST http://localhost:5010/api/ingest/event `
     -H "Content-Type: application/json" `
     -d '{"source": "broken_sensor", "payload": {"error": "No event_type"}}'
```

#### 3. Inspect Live Pipeline Metrics
```powershell
curl http://localhost:5010/api/metrics
```

---

## 5. File Structure

```
08-Injest/
├── app.py                     # Main Flask Ingestion API Server (Port 5010)
├── pipeline.py                # 4-stage ETL Pipeline Engine & DLQ handler
├── init_db.py                 # SQLite schema initialization (ingest_store.db)
├── requirements.txt           # Minimal dependencies (Flask, requests)
├── sample_data/
│   ├── sample_events.csv      # Initial batch records for auto-seeding
│   └── telemetry.json         # Sample JSON stream payload
├── templates/
│   └── dashboard.html         # Real-time Ingestion UI & DLQ Inspector
└── README.md                  # This documentation guide
```

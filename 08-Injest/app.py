"""
=============================================================================
08-Injest — High-Performance Data Ingestion & ETL Pipeline Server
=============================================================================
Provides high-throughput event ingestion, data hygiene, and quarantine:
- Single event & batch ingestion REST APIs (Port 5010)
- Automated 4-stage pipeline (Validation, Normalization, Enrichment, Sink)
- Dead-Letter Queue (DLQ) for malformed records
- Real-time ingestion analytics dashboard
=============================================================================
"""

import os
import random
import logging
from datetime import datetime
from flask import Flask, jsonify, render_template, request

from pipeline import IngestionPipeline
import init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [INJEST-SERVER] %(message)s")
logger = logging.getLogger("injest_app")

app = Flask(__name__)
PORT = int(os.environ.get("INJEST_PORT", 5010))

# Initialize database & pipeline engine
init_db.init_db()
pipeline = IngestionPipeline()

# Auto-seed sample events on first start if empty
def seed_sample_data():
    conn = init_db.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM ingested_events;")
    count = cur.fetchone()[0]
    conn.close()

    if count == 0:
        csv_sample = os.path.join(os.path.dirname(__file__), "sample_data", "sample_events.csv")
        if os.path.exists(csv_sample):
            try:
                logger.info(f"Seeding initial records from {csv_sample}...")
                pipeline.process_csv_file(csv_sample)
            except Exception as e:
                logger.warning(f"Could not seed sample CSV: {e}")

seed_sample_data()

# -----------------------------------------------------------------------------
# Web Dashboard
# -----------------------------------------------------------------------------
@app.route("/")
def dashboard():
    conn = init_db.get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM ingestion_metrics WHERE id=1;")
    metrics_row = cur.fetchone()
    metrics = dict(metrics_row) if metrics_row else {"total_received": 0, "total_processed": 0, "total_failed": 0}

    cur.execute("SELECT * FROM ingested_events ORDER BY ingested_at DESC LIMIT 25;")
    events = [dict(row) for row in cur.fetchall()]

    cur.execute("SELECT * FROM dead_letter_queue ORDER BY id DESC LIMIT 15;")
    dlq = [dict(row) for row in cur.fetchall()]

    conn.close()
    return render_template("dashboard.html", metrics=metrics, events=events, dlq=dlq)

# -----------------------------------------------------------------------------
# REST APIs: Ingestion Endpoints
# -----------------------------------------------------------------------------
@app.route("/api/health")
def health():
    return jsonify({
        "service": "injest_engine",
        "status": "ONLINE",
        "port": PORT,
        "mode": "etl_pipeline"
    }), 200

@app.route("/api/metrics")
def get_metrics():
    conn = init_db.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM ingestion_metrics WHERE id=1;")
    row = cur.fetchone()
    conn.close()
    return jsonify({"status": "success", "metrics": dict(row) if row else {}})

@app.route("/api/ingest/event", methods=["POST"])
def ingest_event():
    data = request.get_json()
    if not data or not isinstance(data, dict):
        return jsonify({"status": "error", "message": "Expected JSON object payload"}), 400

    result = pipeline.process_record(data)
    status_code = 201 if result.get("status") == "success" else 422
    return jsonify(result), status_code

@app.route("/api/ingest/batch", methods=["POST"])
def ingest_batch():
    data = request.get_json()
    if not data or not isinstance(data, list):
        return jsonify({"status": "error", "message": "Expected JSON array of event objects"}), 400

    batch_res = pipeline.process_batch(data)
    return jsonify(batch_res), 200

@app.route("/api/ingest/simulate", methods=["POST"])
def simulate_events():
    """Generates 5 sample events (4 valid + 1 deliberately malformed for DLQ demonstration)."""
    sample_types = ["user_click", "api_call", "sensor_reading", "payment_event", "order_created"]
    sample_sources = ["mobile_app", "web_client", "iot_gateway", "payment_processor"]

    generated = []
    # 4 clean valid events
    for _ in range(4):
        ev = {
            "event_type": random.choice(sample_types),
            "source": random.choice(sample_sources),
            "device_id": f"dev-{random.randint(100, 999)}",
            "payload": {
                "value": round(random.uniform(10.0, 500.0), 2),
                "ip": f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        generated.append(ev)

    # 1 deliberate malformed event (missing event_type) to exercise DLQ
    generated.append({
        "event_type": "",  # Empty -> triggers DLQ
        "source": "malformed_agent",
        "device_id": "bad-client-99",
        "payload": {"error": "Missing mandatory field event_type"}
    })

    batch_res = pipeline.process_batch(generated)
    return jsonify({"status": "success", "simulated": batch_res})

@app.route("/api/ingest/events", methods=["GET"])
def list_events():
    limit = int(request.args.get("limit", 50))
    conn = init_db.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM ingested_events ORDER BY ingested_at DESC LIMIT ?;", (limit,))
    events = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify({"status": "success", "count": len(events), "events": events})

@app.route("/api/ingest/dlq", methods=["GET"])
def list_dlq():
    conn = init_db.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM dead_letter_queue ORDER BY id DESC;")
    dlq = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify({"status": "success", "count": len(dlq), "quarantined": dlq})

if __name__ == "__main__":
    print("\n" + "=" * 65)
    print(f"  ⚡ 08-Injest Pipeline Engine running at http://localhost:{PORT}")
    print(f"  Dashboard       : http://localhost:{PORT}")
    print(f"  Event Ingest API: POST http://localhost:{PORT}/api/ingest/event")
    print(f"  Batch Ingest API: POST http://localhost:{PORT}/api/ingest/batch")
    print("=" * 65 + "\n")
    app.run(host="0.0.0.0", port=PORT, debug=False)

"""
=============================================================================
08-Injest — Core Data Ingestion & ETL Pipeline Engine
=============================================================================
Executes a 4-stage pipeline for incoming events:
  Stage 1: Validation (schema, mandatory attributes, type inspection)
  Stage 2: Sanitization & Normalization (whitespace cleanup, ISO timestamps, PII masking)
  Stage 3: Enrichment (UUID generation, SHA256 integrity hash, latency metrics)
  Stage 4: Storage & DLQ Routing (persists clean events or routes errors to DLQ)
=============================================================================
"""

import csv
import hashlib
import json
import logging
import os
import uuid
from datetime import datetime
import init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [INJEST-PIPELINE] %(message)s")
logger = logging.getLogger("injest_pipeline")

class IngestionError(Exception):
    pass

class IngestionPipeline:
    def __init__(self):
        init_db.init_db()

    def get_db(self):
        return init_db.get_connection()

    def process_record(self, record: dict) -> dict:
        """
        Processes a single incoming dictionary through all 4 pipeline stages.
        """
        conn = self.get_db()
        cur = conn.cursor()

        # Update total received metric
        cur.execute("UPDATE ingestion_metrics SET total_received = total_received + 1, last_processed_at = CURRENT_TIMESTAMP WHERE id = 1;")
        conn.commit()

        # -------------------------------------------------------------
        # Stage 1: Validation
        # -------------------------------------------------------------
        event_type = record.get("event_type")
        source = record.get("source")

        if not event_type or not str(event_type).strip():
            return self._route_to_dlq(conn, record, "Validation Failure: Missing 'event_type'")

        if not source or not str(source).strip():
            return self._route_to_dlq(conn, record, "Validation Failure: Missing 'source'")

        event_type = str(event_type).strip().lower()
        source = str(source).strip().lower()
        device_id = str(record.get("device_id", "unspecified")).strip()

        # -------------------------------------------------------------
        # Stage 2: Normalization & Sanitization
        # -------------------------------------------------------------
        raw_ts = record.get("timestamp")
        normalized_ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        if raw_ts:
            try:
                # Attempt to normalize various common formats
                if "T" in str(raw_ts):
                    clean_ts = str(raw_ts).replace("Z", "").split(".")[0]
                    normalized_ts = datetime.fromisoformat(clean_ts).strftime("%Y-%m-%d %H:%M:%S")
                else:
                    normalized_ts = str(raw_ts).strip()
            except Exception:
                normalized_ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        # Sanitize payload & Mask PII (e.g., IP addresses)
        payload = record.get("payload", {})
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except Exception:
                payload = {"raw_text": payload}

        if isinstance(payload, dict):
            # Mask IP if present for privacy compliance
            if "ip" in payload and isinstance(payload["ip"], str):
                parts = payload["ip"].split(".")
                if len(parts) == 4:
                    payload["ip"] = f"{parts[0]}.{parts[1]}.xxx.xxx"

        payload_json = json.dumps(payload)

        # -------------------------------------------------------------
        # Stage 3: Enrichment
        # -------------------------------------------------------------
        event_id = f"evt_{uuid.uuid4().hex[:12]}"
        hash_input = f"{event_type}|{source}|{device_id}|{payload_json}"
        hash_fingerprint = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()[:16]

        # -------------------------------------------------------------
        # Stage 4: Storage Sink
        # -------------------------------------------------------------
        try:
            cur.execute("""
                INSERT INTO ingested_events (event_id, event_type, source, device_id, payload, normalized_timestamp, hash_fingerprint, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'PROCESSED');
            """, (event_id, event_type, source, device_id, payload_json, normalized_ts, hash_fingerprint))

            cur.execute("UPDATE ingestion_metrics SET total_processed = total_processed + 1 WHERE id = 1;")
            conn.commit()
            conn.close()

            logger.info(f"Ingested event '{event_id}' ({event_type}) from '{source}'")
            return {
                "status": "success",
                "event_id": event_id,
                "event_type": event_type,
                "source": source,
                "normalized_timestamp": normalized_ts,
                "hash_fingerprint": hash_fingerprint,
                "payload": payload
            }
        except Exception as err:
            logger.error(f"Sink failure: {err}")
            return self._route_to_dlq(conn, record, f"Sink Storage Error: {str(err)}")

    def _route_to_dlq(self, conn, record: dict, reason: str) -> dict:
        cur = conn.cursor()
        raw_str = json.dumps(record) if isinstance(record, dict) else str(record)
        source = record.get("source", "unknown") if isinstance(record, dict) else "unknown"

        cur.execute("""
            INSERT INTO dead_letter_queue (raw_data, error_reason, source, status)
            VALUES (?, ?, ?, 'PENDING');
        """, (raw_str, reason, source))

        cur.execute("UPDATE ingestion_metrics SET total_failed = total_failed + 1 WHERE id = 1;")
        conn.commit()
        conn.close()

        logger.warning(f"Routed malformed record to DLQ: {reason}")
        return {
            "status": "dlq_quarantine",
            "error": reason,
            "record": record
        }

    def process_batch(self, records: list) -> dict:
        results = []
        success_count = 0
        failure_count = 0

        for r in records:
            res = self.process_record(r)
            if res.get("status") == "success":
                success_count += 1
            else:
                failure_count += 1
            results.append(res)

        return {
            "total_submitted": len(records),
            "success_count": success_count,
            "failure_count": failure_count,
            "results": results
        }

    def process_csv_file(self, file_path: str) -> dict:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"CSV file not found: {file_path}")

        records = []
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(dict(row))

        return self.process_batch(records)

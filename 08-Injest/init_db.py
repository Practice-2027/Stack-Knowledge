"""
=============================================================================
08-Injest — Database Initialization & Schema
=============================================================================
Configures SQLite storage for:
- Ingested & normalized events sink
- Dead-Letter Queue (DLQ) for malformed records
- Ingestion metrics counters
=============================================================================
"""

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ingest_store.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # 1. Clean Ingested Events Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ingested_events (
            event_id TEXT PRIMARY KEY,
            event_type TEXT NOT NULL,
            source TEXT NOT NULL,
            device_id TEXT,
            payload TEXT,
            normalized_timestamp TIMESTAMP,
            ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            hash_fingerprint TEXT,
            status TEXT DEFAULT 'PROCESSED'
        );
    """)

    # 2. Dead-Letter Queue (DLQ) Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dead_letter_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            raw_data TEXT NOT NULL,
            error_reason TEXT NOT NULL,
            source TEXT DEFAULT 'unknown',
            received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'PENDING'
        );
    """)

    # 3. Ingestion Summary Metrics Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ingestion_metrics (
            id INTEGER PRIMARY KEY,
            total_received INTEGER DEFAULT 0,
            total_processed INTEGER DEFAULT 0,
            total_failed INTEGER DEFAULT 0,
            last_processed_at TIMESTAMP
        );
    """)

    # Ensure single row metrics initialization
    cur.execute("SELECT COUNT(*) FROM ingestion_metrics;")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO ingestion_metrics (id, total_received, total_processed, total_failed) VALUES (1, 0, 0, 0);")

    conn.commit()
    conn.close()
    print("[Injest DB] Database ingest_store.db ready.")

if __name__ == "__main__":
    init_db()

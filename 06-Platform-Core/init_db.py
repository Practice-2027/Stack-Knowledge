"""
=============================================================================
Platform Core — Database Initialization & Seed Data
=============================================================================
Initializes SQLite database schemas for:
- Service Registry & Health Monitoring
- Central Feature Flags & Platform Settings
- Tenant & API Access Management
- Unified Audit Logging
=============================================================================
"""

import os
import sqlite3
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "platform_core.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # 1. Services Registry Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS services (
            name TEXT PRIMARY KEY,
            display_name TEXT NOT NULL,
            host TEXT NOT NULL DEFAULT 'localhost',
            port INTEGER NOT NULL,
            health_path TEXT NOT NULL DEFAULT '/health',
            status TEXT NOT NULL DEFAULT 'OFFLINE',
            last_heartbeat TIMESTAMP,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            category TEXT NOT NULL DEFAULT 'service'
        );
    """)

    # 2. Feature Flags Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS feature_flags (
            flag_key TEXT PRIMARY KEY,
            description TEXT NOT NULL,
            enabled INTEGER NOT NULL DEFAULT 1,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 3. Tenants Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tenants (
            tenant_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            tier TEXT NOT NULL DEFAULT 'STANDARD',
            api_key TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 4. Platform Audit Logs Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            service TEXT NOT NULL,
            actor TEXT NOT NULL DEFAULT 'system',
            details TEXT,
            severity TEXT NOT NULL DEFAULT 'INFO',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()

    # Seed Default Registered Services
    cur.execute("SELECT COUNT(*) FROM services;")
    if cur.fetchone()[0] == 0:
        default_services = [
            ("kafka_queue", "01-Kafka Task Queue", "localhost", 5001, "/health", "UNKNOWN", "messaging"),
            ("keycloak_notes", "02-Keycloak Notes", "localhost", 5002, "/", "UNKNOWN", "security"),
            ("keycloak_auth", "02-Keycloak Server", "localhost", 8088, "/", "UNKNOWN", "identity"),
            ("idp_auth", "03-IDP Auth Server", "localhost", 5003, "/.well-known/openid-configuration", "UNKNOWN", "identity"),
            ("idp_client", "03-IDP Client App", "localhost", 5005, "/", "UNKNOWN", "application"),
            ("rag_service", "04-RAG Document Q&A", "localhost", 5006, "/status", "UNKNOWN", "ai"),
            ("ai_agents", "05-AI-Agents Multi-Agent", "localhost", 5007, "/agents", "UNKNOWN", "ai"),
            ("platform_core", "06-Platform-Core Hub", "localhost", 5008, "/api/health", "ONLINE", "core"),
            ("shell_portal", "07-Shell Application Portal", "localhost", 5009, "/health", "UNKNOWN", "gateway"),
            ("ingest_engine", "08-Injest Pipeline", "localhost", 5010, "/api/health", "UNKNOWN", "data"),
        ]
        cur.executemany("""
            INSERT INTO services (name, display_name, host, port, health_path, status, category)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, default_services)

    # Seed Default Feature Flags
    cur.execute("SELECT COUNT(*) FROM feature_flags;")
    if cur.fetchone()[0] == 0:
        default_flags = [
            ("enable_realtime_ingestion", "Enables stream processing in the ingestion pipeline", 1),
            ("maintenance_mode", "Blocks incoming write requests across client services", 0),
            ("enable_ai_agent_delegation", "Allows orchestrator agents to run sub-agent workflows", 1),
            ("strict_schema_validation", "Rejects non-conforming JSON ingestion payloads to DLQ", 1),
            ("enable_debug_telemetry", "Emits verbose execution metrics in API responses", 1),
        ]
        cur.executemany("""
            INSERT INTO feature_flags (flag_key, description, enabled)
            VALUES (?, ?, ?);
        """, default_flags)

    # Seed Default Tenants
    cur.execute("SELECT COUNT(*) FROM tenants;")
    if cur.fetchone()[0] == 0:
        default_tenants = [
            ("tenant-acme-01", "Acme Corporation", "ENTERPRISE", "key_live_acme98234710"),
            ("tenant-beta-02", "Beta Innovations", "PRO", "key_live_beta48201948"),
            ("tenant-dev-03", "Local Developer Sandbox", "STANDARD", "key_dev_sandbox12345"),
        ]
        cur.executemany("""
            INSERT INTO tenants (tenant_id, name, tier, api_key)
            VALUES (?, ?, ?, ?);
        """, default_tenants)

    # Seed Initial Audit Log
    cur.execute("SELECT COUNT(*) FROM audit_logs;")
    if cur.fetchone()[0] == 0:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("""
            INSERT INTO audit_logs (action, service, actor, details, severity)
            VALUES ('PLATFORM_INIT', 'platform_core', 'system', 'Platform Core database initialized successfully.', 'INFO');
        """)

    conn.commit()
    conn.close()
    print("[Platform-Core DB] Initialized platform_core.db successfully.")

if __name__ == "__main__":
    init_db()

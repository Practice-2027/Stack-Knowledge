"""
=============================================================================
06-Platform-Core — Central Platform Backbone & Service Registry Hub
=============================================================================
Provides central infrastructure services:
- Service Discovery & Health Monitoring Catalog
- Dynamic Feature Flags & Configuration Storage
- Tenant & API Access Key Directory
- Unified Audit Event Logging
- Web Management Dashboard (Port 5008)
=============================================================================
"""

import os
import socket
import sqlite3
import logging
from datetime import datetime
from flask import Flask, jsonify, render_template, request

import init_db

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [PLATFORM-CORE] %(message)s")
logger = logging.getLogger("platform_core")

app = Flask(__name__)
PORT = int(os.environ.get("PLATFORM_CORE_PORT", 5008))

# Ensure database is initialized
init_db.init_db()

def get_db():
    conn = init_db.get_connection()
    return conn

# -----------------------------------------------------------------------------
# Web Dashboard
# -----------------------------------------------------------------------------
@app.route("/")
def dashboard():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM services ORDER BY port ASC;")
    services = [dict(row) for row in cur.fetchall()]

    cur.execute("SELECT * FROM feature_flags ORDER BY flag_key ASC;")
    flags = [dict(row) for row in cur.fetchall()]

    cur.execute("SELECT * FROM tenants ORDER BY created_at DESC;")
    tenants = [dict(row) for row in cur.fetchall()]

    cur.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT 20;")
    audit_logs = [dict(row) for row in cur.fetchall()]
    conn.close()

    return render_template("dashboard.html", services=services, flags=flags, tenants=tenants, audit_logs=audit_logs)

# -----------------------------------------------------------------------------
# REST APIs: Health & Service Discovery
# -----------------------------------------------------------------------------
@app.route("/api/health")
def health():
    return jsonify({
        "service": "platform_core",
        "status": "ONLINE",
        "port": PORT,
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route("/api/registry/services", methods=["GET"])
def list_services():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM services ORDER BY port ASC;")
    services = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify({"status": "success", "count": len(services), "services": services})

@app.route("/api/registry/register", methods=["POST"])
def register_service():
    data = request.get_json() or {}
    name = data.get("name")
    display_name = data.get("display_name", name)
    host = data.get("host", "localhost")
    port = data.get("port")
    health_path = data.get("health_path", "/health")
    category = data.get("category", "microservice")

    if not name or not port:
        return jsonify({"status": "error", "message": "name and port are required"}), 400

    conn = get_db()
    cur = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("""
        INSERT INTO services (name, display_name, host, port, health_path, status, last_heartbeat, category)
        VALUES (?, ?, ?, ?, ?, 'ONLINE', ?, ?)
        ON CONFLICT(name) DO UPDATE SET
            display_name=excluded.display_name,
            host=excluded.host,
            port=excluded.port,
            health_path=excluded.health_path,
            status='ONLINE',
            last_heartbeat=excluded.last_heartbeat,
            category=excluded.category;
    """, (name, display_name, host, port, health_path, now_str, category))
    conn.commit()
    conn.close()

    logger.info(f"Registered service '{name}' at http://{host}:{port}")
    return jsonify({"status": "success", "message": f"Service '{name}' registered"}), 201

@app.route("/api/registry/probe", methods=["POST"])
def probe_services():
    """Checks port connectivity for all registered services and updates status."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT name, host, port FROM services;")
    services = cur.fetchall()

    updated = []
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for s in services:
        name, host, port = s["name"], s["host"], s["port"]
        is_online = False
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(0.3)
                is_online = (sock.connect_ex((host, port)) == 0)
        except Exception:
            is_online = False

        status = "ONLINE" if is_online else "OFFLINE"
        cur.execute("UPDATE services SET status=?, last_heartbeat=? WHERE name=?;", (status, now_str, name))
        updated.append({"name": name, "port": port, "status": status})

    conn.commit()
    conn.close()
    return jsonify({"status": "success", "probed": len(updated), "results": updated})

# -----------------------------------------------------------------------------
# REST APIs: Dynamic Feature Flags
# -----------------------------------------------------------------------------
@app.route("/api/flags", methods=["GET"])
def get_flags():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM feature_flags;")
    flags = {row["flag_key"]: bool(row["enabled"]) for row in cur.fetchall()}
    conn.close()
    return jsonify({"status": "success", "flags": flags})

@app.route("/api/flags/toggle", methods=["POST"])
def toggle_flag():
    data = request.get_json() or {}
    key = data.get("flag_key")
    enabled = int(data.get("enabled", 1))

    if not key:
        return jsonify({"status": "error", "message": "flag_key is required"}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE feature_flags SET enabled=?, updated_at=CURRENT_TIMESTAMP WHERE flag_key=?;", (enabled, key))
    cur.execute("""
        INSERT INTO audit_logs (action, service, actor, details, severity)
        VALUES ('FLAG_TOGGLE', 'platform_core', 'admin', ?, 'INFO');
    """, (f"Flag '{key}' changed to {enabled}",))
    conn.commit()
    conn.close()

    logger.info(f"Feature flag '{key}' updated to {enabled}")
    return jsonify({"status": "success", "flag_key": key, "enabled": enabled})

# -----------------------------------------------------------------------------
# REST APIs: Audit Logging
# -----------------------------------------------------------------------------
@app.route("/api/audit", methods=["GET", "POST"])
def audit():
    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        data = request.get_json() or {}
        action = data.get("action", "EVENT")
        service = data.get("service", "unknown")
        actor = data.get("actor", "system")
        details = data.get("details", "")
        severity = data.get("severity", "INFO")

        cur.execute("""
            INSERT INTO audit_logs (action, service, actor, details, severity)
            VALUES (?, ?, ?, ?, ?);
        """, (action, service, actor, details, severity))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Audit event recorded"}), 201

    limit = int(request.args.get("limit", 50))
    cur.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT ?;", (limit,))
    logs = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify({"status": "success", "count": len(logs), "audit_logs": logs})

# -----------------------------------------------------------------------------
# REST APIs: Tenants & Key Verification
# -----------------------------------------------------------------------------
@app.route("/api/tenants/verify", methods=["POST"])
def verify_api_key():
    data = request.get_json() or {}
    api_key = data.get("api_key")
    if not api_key:
        return jsonify({"status": "error", "valid": False, "message": "api_key required"}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT tenant_id, name, tier FROM tenants WHERE api_key=?;", (api_key,))
    tenant = cur.fetchone()
    conn.close()

    if tenant:
        return jsonify({"status": "success", "valid": True, "tenant": dict(tenant)})
    return jsonify({"status": "error", "valid": False, "message": "Invalid API Key"}), 401

if __name__ == "__main__":
    print("\n" + "=" * 65)
    print(f"  🏛️ 06-Platform-Core running at http://localhost:{PORT}")
    print(f"  Dashboard       : http://localhost:{PORT}")
    print(f"  Service Registry: http://localhost:{PORT}/api/registry/services")
    print(f"  Feature Flags   : http://localhost:{PORT}/api/flags")
    print("=" * 65 + "\n")
    app.run(host="0.0.0.0", port=PORT, debug=False)

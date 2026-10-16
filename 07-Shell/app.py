"""
=============================================================================
07-Shell — Micro-Frontend Portal & Reverse Proxy API Gateway
=============================================================================
Serves as the unified front door for the enterprise architecture:
- Single-Pane-of-Glass unified management portal (Port 5009)
- Reverse proxy gateway routing requests downstream across all microservices
- Multi-tenant context injection (X-Tenant-ID)
- Real-time service connectivity health probe
=============================================================================
"""

import os
import socket
import logging
import requests
from flask import Flask, jsonify, render_template, request, Response

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [SHELL-GATEWAY] %(message)s")
logger = logging.getLogger("shell")

app = Flask(__name__)
PORT = int(os.environ.get("SHELL_PORT", 5009))

# Downstream Service Port Registry Map
SERVICE_MAP = {
    "platform": {"name": "06-Platform-Core Hub", "host": "localhost", "port": 5008},
    "ingest": {"name": "08-Injest Pipeline Engine", "host": "localhost", "port": 5010},
    "kafka": {"name": "01-Kafka Task Queue", "host": "localhost", "port": 5001},
    "notes": {"name": "02-Keycloak Notes App", "host": "localhost", "port": 5002},
    "auth": {"name": "02-Keycloak Identity Server", "host": "localhost", "8088": 8088, "port": 8088},
    "idp": {"name": "03-IDP Custom Identity Server", "host": "localhost", "port": 5003},
    "client": {"name": "03-IDP Client Application", "host": "localhost", "port": 5005},
    "rag": {"name": "04-RAG Vector Search", "host": "localhost", "port": 5006},
    "agents": {"name": "05-AI-Agents Multi-Agent", "host": "localhost", "port": 5007},
}

def probe_port(host: str, port: int, timeout: float = 0.2) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            return sock.connect_ex((host, port)) == 0
    except Exception:
        return False

# -----------------------------------------------------------------------------
# Web Portal UI
# -----------------------------------------------------------------------------
@app.route("/")
def portal():
    services_status = []
    for key, info in SERVICE_MAP.items():
        online = probe_port(info["host"], info["port"])
        services_status.append({
            "key": key,
            "name": info["name"],
            "host": info["host"],
            "port": info["port"],
            "online": online,
        })
    return render_template("portal.html", services=services_status)

@app.route("/health")
def health():
    return jsonify({
        "service": "shell_portal",
        "status": "ONLINE",
        "port": PORT,
        "mode": "api_gateway_and_portal"
    }), 200

# -----------------------------------------------------------------------------
# Transparent API Gateway Reverse Proxy
# -----------------------------------------------------------------------------
@app.route("/gateway/<service_key>/<path:subpath>", methods=["GET", "POST", "PUT", "DELETE"])
def gateway_proxy(service_key, subpath):
    if service_key not in SERVICE_MAP:
        return jsonify({
            "status": "error",
            "message": f"Service key '{service_key}' not found in Shell Gateway registry.",
            "available_services": list(SERVICE_MAP.keys())
        }), 404

    target = SERVICE_MAP[service_key]
    target_url = f"http://{target['host']}:{target['port']}/{subpath}"
    
    # Check if service is listening before attempting proxy
    if not probe_port(target["host"], target["port"]):
        return jsonify({
            "status": "error",
            "message": f"Target service '{target['name']}' is offline at http://{target['host']}:{target['port']}",
            "hint": f"Launch the service using run.cmd"
        }), 503

    # Forward headers and inject tenant context
    headers = {k: v for k, v in request.headers if k.lower() not in ["host", "content-length"]}
    headers["X-Gateway-Forwarded"] = "07-Shell-Portal-v1.0"
    tenant_id = request.headers.get("X-Tenant-ID", "tenant-dev-03")
    headers["X-Tenant-ID"] = tenant_id

    try:
        resp = requests.request(
            method=request.method,
            url=target_url,
            headers=headers,
            params=request.args,
            data=request.get_data(),
            timeout=10,
        )
        return Response(
            resp.content,
            status=resp.status_code,
            content_type=resp.headers.get("content-type", "application/json")
        )
    except Exception as ex:
        logger.error(f"Gateway proxy error to {target_url}: {ex}")
        return jsonify({
            "status": "error",
            "message": f"Gateway proxy failure calling {target_url}: {str(ex)}"
        }), 502

if __name__ == "__main__":
    print("\n" + "=" * 65)
    print(f"  🌐 07-Shell Portal & Gateway running at http://localhost:{PORT}")
    print(f"  Portal UI      : http://localhost:{PORT}")
    print(f"  Gateway Router : http://localhost:{PORT}/gateway/<service>/<path>")
    print("=" * 65 + "\n")
    app.run(host="0.0.0.0", port=PORT, debug=False)

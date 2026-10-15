"""
=============================================================================
ALL STACKS - Master Cross-Platform Project Orchestrator
=============================================================================
Runs all 5 tech stack projects simultaneously in the terminal:
- 01-Kafka: Task Queue Producer (5001) & Consumer Worker
- 02-Keycloak: Secure Notes App (5002) & OIDC Identity Server (8088)
- 03-IDP: Custom Auth Server (5003), Resource API (5004), Client (5005)
- 04-RAG: Document Q&A Vector Retrieval System (5006)
- 05-AI-Agents: Multi-Agent Automation System (5007)

Usage:
    python run_all.py
=============================================================================
"""

import os
import sys
import time
import subprocess
import webbrowser

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

SERVICES = [
    {
        "name": "01-Kafka Consumer",
        "cwd": os.path.join(ROOT_DIR, "01-Kafka"),
        "cmd": [sys.executable, "consumer.py"],
        "port": None,
        "color": "\033[93m",
    },
    {
        "name": "01-Kafka Producer",
        "cwd": os.path.join(ROOT_DIR, "01-Kafka"),
        "cmd": [sys.executable, "producer.py"],
        "port": 5001,
        "color": "\033[92m",
    },
    {
        "name": "02-Keycloak Notes",
        "cwd": os.path.join(ROOT_DIR, "02-Keycloak"),
        "cmd": [sys.executable, "app.py"],
        "port": 5002,
        "color": "\033[95m",
    },
    {
        "name": "03-IDP Ecosystem",
        "cwd": os.path.join(ROOT_DIR, "03-IDP"),
        "cmd": [sys.executable, "run_all.py"],
        "port": 5005,
        "color": "\033[91m",
    },
    {
        "name": "04-RAG System",
        "cwd": os.path.join(ROOT_DIR, "04-RAG"),
        "cmd": [sys.executable, "app.py"],
        "port": 5006,
        "color": "\033[96m",
    },
    {
        "name": "05-AI-Agents",
        "cwd": os.path.join(ROOT_DIR, "05-AI-Agents"),
        "cmd": [sys.executable, "run.py"],
        "port": 5007,
        "color": "\033[94m",
    },
]

DASHBOARDS = [
    ("01-Kafka Task Queue", "http://localhost:5001"),
    ("02-Keycloak Secure Notes", "http://localhost:5002"),
    ("02-Keycloak Auth & Admin", "http://localhost:8088"),
    ("03-IDP Client Application", "http://localhost:5005"),
    ("04-RAG Document Q&A", "http://localhost:5006"),
    ("05-AI-Agents Orchestrator", "http://localhost:5007"),
]

def main():
    print("\n" + "=" * 70)
    print("  🚀 ALL STACKS - MASTER PROJECT RUNNER")
    print("  Starting all 5 projects concurrently...")
    print("=" * 70)
    print("\n  Allocated Service Endpoints:")
    for name, url in DASHBOARDS:
        print(f"    • {name:<26} -> {url}")
    print("=" * 70 + "\n")

    processes = []
    try:
        for s in SERVICES:
            print(f"  [+] Starting {s['name']} (cwd: {os.path.basename(s['cwd'])})...")
            p = subprocess.Popen(
                s["cmd"],
                cwd=s["cwd"],
                stdout=subprocess.DEVNULL if s["port"] in [5001, 5006, 5007] else None,
                stderr=None,
            )
            processes.append((s["name"], p))
            time.sleep(1)

        print("\n" + "=" * 70)
        print("  ✅ All 5 projects are running in the background!")
        print("  Press Ctrl+C at any time in this window to stop all services.")
        print("=" * 70 + "\n")

        # Open web dashboards in browser
        time.sleep(2)
        print("  Opening dashboards in browser...")
        for _, url in DASHBOARDS:
            if not url.endswith("8088"):  # Open main apps
                webbrowser.open(url)

        # Monitor loop
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n  🛑 Stopping all projects...")
        for name, p in processes:
            try:
                p.terminate()
            except Exception:
                pass
        print("  [OK] All projects stopped cleanly.\n")

if __name__ == "__main__":
    main()

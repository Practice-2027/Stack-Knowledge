"""
run.py
======
Primary entry point for the Multi-Agent Task Automation System.

Initializes:
  - Central MessageBus
  - Specialist Agents (Orchestrator, Researcher, Calculator, Writer, FileAgent)
  - Tool Registries (15+ tools across math, file, research, and text)
  - Pre-loaded workspace files (sales.csv, employees.txt)
  - Flask web server on port 5007

Usage:
  python run.py
"""

from __future__ import annotations
import os
import sys

# Ensure UTF-8 output on Windows PowerShell / CMD
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from app import app, message_bus, orchestrator
from tools import get_all_tools


def print_startup_banner(port: int):
    """Prints a friendly beginner console banner."""
    tools_count = len(get_all_tools())
    agents_count = len(message_bus.agents)
    
    border = "=" * 76
    print("\n" + border)
    print("   🤖  MULTI-AGENT TASK AUTOMATION SYSTEM — BEGINNER EDITION  🤖")
    print(border)
    print(f"  * Status:              ONLINE")
    print(f"  * Registered Agents:   {agents_count} specialized agents")
    for name, agent in message_bus.agents.items():
        print(f"     - {name:<14} : {agent.role}")
    print(f"  * Active Tools:        {tools_count} real local tools (no paid API keys required)")
    print(f"  * Message Bus:         In-memory decoupled message broker with thread safety")
    print(f"  * Web Dashboard:       http://localhost:{port}")
    print(f"  * Workspace Directory: {os.path.abspath('workspace')}")
    print(border)
    print("  Quick Start:")
    print(f"    1. Open your browser at http://localhost:{port}")
    print(f"    2. Click any of the 4 pre-built example scenarios")
    print(f"    3. Watch agents exchange messages and collaborate in real time!")
    print(border + "\n")


def main():
    port = int(os.environ.get("PORT", 5007))
    print_startup_banner(port)
    # Start Flask Web Server
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()

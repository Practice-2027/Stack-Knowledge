"""
app.py
======
Flask Web Application for the Multi-Agent Task Automation System.
Runs an interactive dashboard on http://localhost:5007.

Endpoints:
  GET  /             - Dashboard UI showing agent swarm, message feed, and task runner
  POST /task         - Submit task for multi-agent delegation & execution
  GET  /history      - Return chronological task execution history (JSON)
  GET  /agents       - Return list of registered agents, statuses, and capabilities (JSON)
  GET  /messages     - Return MessageBus communication log (JSON)
  GET  /files        - List workspace files and metadata (JSON)
  GET  /file/<name>  - Inspect workspace file content (JSON)
  POST /reset        - Reset message history and task log
"""

from __future__ import annotations
import os
import sys
from typing import Dict, Any
from flask import Flask, render_template, request, jsonify

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from agent_framework import MessageBus
from agents import (
    OrchestratorAgent,
    ResearcherAgent,
    CalculatorAgent,
    WriterAgent,
    FileAgent,
)
from tools import list_files, read_file

# Initialize Flask application
app = Flask(__name__, template_folder="templates")

# Initialize global Multi-Agent Infrastructure
message_bus = MessageBus()
orchestrator = OrchestratorAgent()
researcher = ResearcherAgent()
calculator = CalculatorAgent()
writer = WriterAgent()
file_agent = FileAgent()

# Register all agents onto the central MessageBus
for agent_instance in [orchestrator, researcher, calculator, writer, file_agent]:
    message_bus.register_agent(agent_instance)


@app.route("/", methods=["GET"])
def dashboard():
    """Render the primary interactive agent swarm dashboard."""
    return render_template("dashboard.html")


@app.route("/task", methods=["POST"])
def submit_task():
    """
    Submit a task for orchestration.
    Accepts JSON payload: {"task": "..."} or form-encoded "task" field.
    """
    if request.is_json:
        data = request.get_json() or {}
        task_str = data.get("task", "").strip()
    else:
        task_str = request.form.get("task", "").strip()

    if not task_str:
        return jsonify({"error": "Task description cannot be empty."}), 400

    print(f"\n[Flask HTTP POST /task] Received: '{task_str}'")
    result = orchestrator.process_task(task_str)
    return jsonify(result)


@app.route("/history", methods=["GET"])
def get_task_history():
    """Return list of all executed tasks and their deliverables."""
    return jsonify(orchestrator.task_history)


@app.route("/agents", methods=["GET"])
def get_agents():
    """Return all registered agents with their live statuses and capabilities."""
    statuses = [agent.get_status() for agent in message_bus.agents.values()]
    return jsonify(statuses)


@app.route("/messages", methods=["GET"])
def get_messages():
    """
    Return message bus history with optional filtering.
    Query params:
      - agent: filter sender or receiver by name
      - type: filter by TASK, RESULT, INFO, ERROR
      - limit: maximum messages to return (default 100)
    """
    agent_filter = request.args.get("agent")
    type_filter = request.args.get("type")
    limit = int(request.args.get("limit", 150))

    messages = message_bus.get_messages(
        agent_name=agent_filter,
        message_type=type_filter,
        limit=limit,
    )
    return jsonify(messages)


@app.route("/files", methods=["GET"])
def list_workspace_files():
    """Return list of files present in the workspace directory."""
    try:
        files_data = list_files()
        return jsonify(files_data)
    except Exception as exc:
        return jsonify({"error": str(exc), "files": []}), 500


@app.route("/file/<filename>", methods=["GET"])
def view_workspace_file(filename: str):
    """Safely return content of a designated workspace file."""
    try:
        file_data = read_file(filename=filename)
        return jsonify(file_data)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 404


@app.route("/reset", methods=["POST"])
def reset_system():
    """Clear message bus logs and task history."""
    message_bus.clear_history()
    orchestrator.task_history.clear()
    for agent in message_bus.agents.values():
        agent.status = "IDLE"
    return jsonify({"message": "System reset successfully."})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5007))
    print(f"\nStarting Multi-Agent System on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)

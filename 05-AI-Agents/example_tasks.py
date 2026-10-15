"""
example_tasks.py
================
Pre-built demonstration tasks showcasing specialized multi-agent collaboration.

Includes:
  1. Renewable Energy Research & Report (Researcher + Writer)
  2. Compound Interest Calculation & Projections (Calculator + Writer)
  3. Sales CSV Analysis & Summary (FileAgent + Calculator + Writer + FileAgent)
  4. Python Programming Beginner Guide (Researcher + Writer)

Can be imported into the web UI or run directly from the command line:
    python example_tasks.py
"""

from __future__ import annotations
import sys
import time
from typing import Dict, List, Any

# Ensure UTF-8 output in Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Define the canonical example tasks
EXAMPLE_TASKS: List[Dict[str, Any]] = [
    {
        "id": "renewable_energy",
        "title": "Renewable Energy Research & Report",
        "task": "Research and write a report about renewable energy",
        "category": "Domain Knowledge Research & Reporting",
        "involved_agents": ["Orchestrator", "Researcher", "Writer"],
        "description": (
            "The Orchestrator delegates deep topic investigation to the Researcher, "
            "which queries the knowledge base and simulated web index. "
            "The Writer then compiles the findings into an executive markdown briefing."
        ),
        "icon": "[RESEARCH]",
    },
    {
        "id": "compound_interest",
        "title": "Compound Interest Financial Modeling",
        "task": "Calculate compound interest for $10000 at 5% for 10 years",
        "category": "Financial Growth Modeling",
        "involved_agents": ["Orchestrator", "Calculator", "Writer"],
        "description": (
            "The Orchestrator extracts financial parameters ($10k principal, 5% annual rate, 10 years) "
            "and dispatches to the Calculator agent. The Calculator computes terminal balance and "
            "annual accruals. The Writer generates an amortization schedule and executive memo."
        ),
        "icon": "[FINANCE]",
    },
    {
        "id": "sales_analysis",
        "title": "Sales CSV Ingestion & Executive Summary",
        "task": "Read data from workspace/sales.csv and create a summary report",
        "category": "Sales Data Analytics & Reporting",
        "involved_agents": ["Orchestrator", "FileAgent", "Calculator", "Writer"],
        "description": (
            "A 4-step pipeline: FileAgent reads and parses workspace/sales.csv; "
            "Calculator computes descriptive revenue statistics (mean, total, variance); "
            "Writer produces a sales KPI report; FileAgent writes the report to workspace/sales_summary_report.md."
        ),
        "icon": "[DATA]",
    },
    {
        "id": "python_guide",
        "title": "Python Programming Beginner Guide",
        "task": "Research Python programming and create a beginner guide",
        "category": "Technical Education & Guide Authoring",
        "involved_agents": ["Orchestrator", "Researcher", "Writer"],
        "description": (
            "The Orchestrator commands the Researcher to retrieve Python language specifications, "
            "PEP standards, and history. The Writer synthesizes a starter roadmap with code snippets "
            "and learning milestones."
        ),
        "icon": "[GUIDE]",
    },
]


def setup_multi_agent_system():
    """Initializes and connects all agents to a fresh MessageBus."""
    from agent_framework import MessageBus
    from agents import (
        OrchestratorAgent,
        ResearcherAgent,
        CalculatorAgent,
        WriterAgent,
        FileAgent,
    )

    bus = MessageBus()
    orchestrator = OrchestratorAgent()
    researcher = ResearcherAgent()
    calculator = CalculatorAgent()
    writer = WriterAgent()
    file_agent = FileAgent()

    for agent in [orchestrator, researcher, calculator, writer, file_agent]:
        bus.register_agent(agent)

    return bus, orchestrator


def run_single_example(example_index: int) -> Dict[str, Any]:
    """Execute a single example task by index (0-3)."""
    if example_index < 0 or example_index >= len(EXAMPLE_TASKS):
        raise IndexError(f"Example index {example_index} is out of bounds.")

    example = EXAMPLE_TASKS[example_index]
    print(f"\n{'#'*75}")
    print(f"# RUNNING EXAMPLE {example_index + 1}: {example['title']}")
    print(f"# Task: \"{example['task']}\"")
    print(f"# Participating Agents: {', '.join(example['involved_agents'])}")
    print(f"{'#'*75}\n")

    bus, orchestrator = setup_multi_agent_system()
    result = orchestrator.process_task(example["task"])

    print(f"\n{'-'*75}")
    print(f"[RESULT PREVIEW] Key Deliverable: {result.get('key_deliverable')}")
    print(f"[RESULT PREVIEW] Duration: {result.get('duration_seconds')} seconds")
    print(f"[RESULT PREVIEW] Steps Executed: {len(result.get('execution_trace', []))}")
    if result.get("artifacts_created"):
        print(f"[RESULT PREVIEW] Artifacts Written to Disk: {result.get('artifacts_created')}")
    print(f"{'-'*75}\n")

    return result


def run_all_cli():
    """Runs all 4 example tasks sequentially via the terminal."""
    print("\n" + "=" * 75)
    print("      MULTI-AGENT AUTOMATION SYSTEM - CLI DEMONSTRATION SUITE")
    print("=" * 75)
    print(f"Total Example Scenarios: {len(EXAMPLE_TASKS)}")

    for i, ex in enumerate(EXAMPLE_TASKS):
        print(f"  [{i + 1}] {ex['icon']} {ex['title']}")
        print(f"      Prompt: \"{ex['task']}\"")

    print("\nStarting execution of all scenarios...\n")

    for i in range(len(EXAMPLE_TASKS)):
        run_single_example(i)
        time.sleep(1)

    print("\n" + "=" * 75)
    print("  ALL 4 MULTI-AGENT EXAMPLE SCENARIOS EXECUTED SUCCESSFULLY!")
    print("=" * 75 + "\n")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        idx = int(sys.argv[1]) - 1
        run_single_example(idx)
    else:
        run_all_cli()

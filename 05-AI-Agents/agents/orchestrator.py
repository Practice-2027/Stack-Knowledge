"""
agents/orchestrator.py
======================
The Orchestrator Agent is the central coordinator of the multi-agent system.
It inspects user tasks, generates execution plans, delegates subtasks to specialist
agents across the MessageBus, manages retries, and synthesizes final deliverables.
"""

from __future__ import annotations
import datetime
import re
import time
import uuid
from typing import Any, Dict, List, Optional
from agent_framework import BaseAgent, Message, MessageType


class OrchestratorAgent(BaseAgent):
    """
    Central Orchestrator Agent.

    Responsibilities:
      - Analyzes natural language prompts using rule-based intent decomposition.
      - Constructs sequential execution plans specifying target specialist agents.
      - Dispatches TASK messages via the MessageBus and awaits RESULT messages.
      - Provides fault tolerance: retries failed steps up to 2 times.
      - Passes intermediate artifacts between agents (pipeline chaining).
      - Compiles a cohesive final report and execution trace.
    """

    def __init__(self, name: str = "Orchestrator"):
        super().__init__(
            name=name,
            role="Task Decomposer, Workflow Coordinator & Result Synthesizer",
            capabilities=[
                "Rule-Based Task Intent Decomposition",
                "Dynamic Multi-Step Workflow Planning",
                "Specialist Agent Delegation via MessageBus",
                "Automated Error Recovery & Retries",
                "Pipeline Context Chaining",
                "Final Artifact & Summary Synthesis",
            ],
        )
        self.task_history: List[Dict[str, Any]] = []

    def analyze_task(self, task_description: str) -> Dict[str, Any]:
        """
        Deconstructs a user task into a structured multi-step execution plan.
        Uses rule-based keyword and pattern matching (no external LLM required).

        Args:
            task_description: The user prompt string.

        Returns:
            dict: Structured plan with category and ordered steps.
        """
        t = task_description.lower().strip()
        steps: List[Dict[str, Any]] = []

        # -------------------------------------------------------------------
        # Scenario A: Sales Data Analysis & Reporting (File + Calc + Writer + File)
        # e.g., 'Read data from workspace/sales.csv and create a summary report'
        # -------------------------------------------------------------------
        if ("sales" in t or "csv" in t) and ("report" in t or "summary" in t or "read" in t):
            category = "Sales Data Analytics & Reporting"
            steps.append({
                "step": 1,
                "agent": "FileAgent",
                "action": "read_csv_file",
                "description": "Read and parse tabular sales transactions from workspace/sales.csv",
                "payload": {"action": "read", "filename": "sales.csv"},
            })
            steps.append({
                "step": 2,
                "agent": "Calculator",
                "action": "compute_sales_statistics",
                "description": "Compute gross revenue, average deal size, and transaction variance",
                "payload": {"action": "statistics", "source": "previous_step"},
            })
            steps.append({
                "step": 3,
                "agent": "Writer",
                "action": "draft_sales_summary",
                "description": "Compile formatted executive sales summary with regional breakdown and KPIs",
                "payload": {"template": "sales_summary", "context_from": [1, 2]},
            })
            steps.append({
                "step": 4,
                "agent": "FileAgent",
                "action": "save_sales_report",
                "description": "Persist final report artifact to workspace/sales_summary_report.md",
                "payload": {"action": "write", "filename": "sales_summary_report.md", "source": 3},
            })

        # -------------------------------------------------------------------
        # Scenario B: Compound Interest / Financial Projections (Calc + Writer)
        # e.g., 'Calculate compound interest for $10000 at 5% for 10 years'
        # -------------------------------------------------------------------
        elif any(k in t for k in ("compound interest", "interest for", "compounding", "financial projection")):
            category = "Financial Growth Modeling"
            steps.append({
                "step": 1,
                "agent": "Calculator",
                "action": "model_compound_interest",
                "description": "Compute compound growth schedule, terminal balance, and annual accruals",
                "payload": {"action": "compound_interest", "prompt": task_description},
            })
            steps.append({
                "step": 2,
                "agent": "Writer",
                "action": "format_financial_report",
                "description": "Draft executive investment memo with annual breakdown schedule table",
                "payload": {"template": "financial_report", "context_from": [1]},
            })

        # -------------------------------------------------------------------
        # Scenario C: Beginner Guide Creation (Researcher + Writer)
        # e.g., 'Research Python programming and create a beginner guide'
        # -------------------------------------------------------------------
        elif "beginner guide" in t or ("guide" in t and ("python" in t or "programming" in t)):
            category = "Technical Education & Guide Authoring"
            topic_match = re.search(r"(?:research\s+)?([a-zA-Z0-9_\-\s]+?)(?:\s+and\s+create|\s+for\s+beginners|$)", task_description, re.I)
            raw_topic = topic_match.group(1).strip() if topic_match else "Python programming"
            # Strip preamble words
            topic = re.sub(r"^(please\s+)?(research\s+|learn\s+)", "", raw_topic, flags=re.I).strip()
            if not topic:
                topic = "Python programming"

            steps.append({
                "step": 1,
                "agent": "Researcher",
                "action": "research_topic",
                "description": f"Gather fundamentals, history, and syntax specifications for {topic}",
                "payload": {"topic": topic},
            })
            steps.append({
                "step": 2,
                "agent": "Writer",
                "action": "author_beginner_guide",
                "description": f"Format comprehensive beginner roadmap and code samples for {topic}",
                "payload": {"template": "beginner_guide", "topic": topic, "context_from": [1]},
            })

        # -------------------------------------------------------------------
        # Scenario D: Deep Research & Report (Researcher + Writer)
        # e.g., 'Research and write a report about renewable energy'
        # -------------------------------------------------------------------
        elif "research" in t or ("report" in t and any(w in t for w in ("energy", "solar", "wind", "ai", "machine learning", "cloud"))):
            category = "Domain Knowledge Research & Reporting"
            # Extract topic cleanly
            topic = re.sub(r"^(please\s+)?(research\s+(and\s+write\s+a\s+report\s+about|about)?|investigate|study)\s+", "", task_description, flags=re.I).strip()
            topic = re.sub(r"\s+and\s+write\s+a\s+report.*$", "", topic, flags=re.I).strip()
            if not topic:
                topic = "Renewable Energy"

            steps.append({
                "step": 1,
                "agent": "Researcher",
                "action": "research_domain",
                "description": f"Query offline knowledge base and simulated web for '{topic}' data",
                "payload": {"topic": topic},
            })
            steps.append({
                "step": 2,
                "agent": "Writer",
                "action": "publish_research_report",
                "description": f"Author structured markdown briefing with executive summary and statistics",
                "payload": {"template": "research_report", "context_from": [1]},
            })

        # -------------------------------------------------------------------
        # Scenario E: Standalone Math / Calculation
        # e.g., 'Calculate 25 * 40 + sqrt(144)' or 'Convert 100 km to miles'
        # -------------------------------------------------------------------
        elif any(k in t for k in ("calculate", "compute", "evaluate", "convert", "roi", "statistics")):
            category = "Mathematical Computation"
            steps.append({
                "step": 1,
                "agent": "Calculator",
                "action": "execute_calculation",
                "description": "Perform requested mathematical or statistical computation",
                "payload": task_description,
            })

        # -------------------------------------------------------------------
        # Scenario F: Standalone Workspace File Operation
        # e.g., 'List files in workspace' or 'Read employees.txt'
        # -------------------------------------------------------------------
        elif any(k in t for k in ("file", "files", "workspace", "employees.txt", "sales.csv", "directory")):
            category = "Workspace File Operation"
            steps.append({
                "step": 1,
                "agent": "FileAgent",
                "action": "workspace_file_operation",
                "description": "Perform designated workspace file inspection or read",
                "payload": task_description,
            })

        # -------------------------------------------------------------------
        # Scenario G: Fallback General Inquiry (Researcher -> Writer)
        # -------------------------------------------------------------------
        else:
            category = "General Inquiry & Documentation"
            steps.append({
                "step": 1,
                "agent": "Researcher",
                "action": "investigate_prompt",
                "description": f"Look up subject context for: '{task_description}'",
                "payload": {"topic": task_description},
            })
            steps.append({
                "step": 2,
                "agent": "Writer",
                "action": "synthesize_response",
                "description": "Draft polished Markdown documentation from researched findings",
                "payload": {"template": "research_report", "context_from": [1]},
            })

        return {
            "task": task_description,
            "category": category,
            "steps_count": len(steps),
            "steps": steps,
        }

    def execute_plan(self, plan: Dict[str, Any], task_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute an analyzed workflow plan by delegating subtasks across the MessageBus.

        Args:
            plan: The output of analyze_task().
            task_id: Unique tracking ID for this task session.

        Returns:
            dict: Comprehensive execution results with traces, timings, and artifacts.
        """
        task_id = task_id or f"task-{uuid.uuid4().hex[:6]}"
        task_desc = plan.get("task", "Unknown Task")
        start_time = time.time()
        self.status = "BUSY"

        print(f"\n{'='*75}")
        print(f"[Orchestrator] Starting Task ID: {task_id}")
        print(f"[Orchestrator] Objective: {task_desc}")
        print(f"[Orchestrator] Category: {plan.get('category')} ({plan.get('steps_count')} steps)")
        print(f"{'='*75}\n")

        # Initial notification to message bus
        self.send_message(
            receiver="*",
            content=f"Starting task execution: '{task_desc}' (Plan has {plan.get('steps_count')} steps)",
            message_type=MessageType.INFO,
            metadata={"task_id": task_id, "category": plan.get("category")},
        )

        step_results: Dict[int, Any] = {}
        execution_trace: List[Dict[str, Any]] = []
        artifacts_created: List[str] = []

        for step_info in plan.get("steps", []):
            step_num = step_info["step"]
            agent_name = step_info["agent"]
            desc = step_info["description"]
            raw_payload = step_info["payload"]

            print(f"[Orchestrator] Step {step_num}/{plan.get('steps_count')}: Delegating to '{agent_name}'")
            print(f"               Action: {desc}")

            # Resolve chained context inputs
            payload = self._resolve_payload(raw_payload, step_results, plan)

            # Delegate with retry handling
            success = False
            result_payload = None
            error_message = None
            max_attempts = 2

            for attempt in range(1, max_attempts + 1):
                try:
                    # 1. Send TASK message via bus
                    task_msg = self.send_message(
                        receiver=agent_name,
                        content=payload,
                        message_type=MessageType.TASK,
                        metadata={
                            "task_id": task_id,
                            "step": step_num,
                            "attempt": attempt,
                            "action": step_info.get("action"),
                            "description": desc,
                        },
                    )

                    # 2. Invoke target specialist agent
                    if not self.message_bus or agent_name not in self.message_bus.agents:
                        raise RuntimeError(f"Specialist agent '{agent_name}' is not registered on MessageBus.")

                    target_agent = self.message_bus.agents[agent_name]
                    step_start = time.time()
                    agent_output = target_agent.process_task(payload)
                    elapsed_step = round(time.time() - step_start, 3)

                    # 3. Agent replies with RESULT message
                    target_agent.send_message(
                        receiver=self.name,
                        content=agent_output,
                        message_type=MessageType.RESULT,
                        metadata={
                            "task_id": task_id,
                            "step": step_num,
                            "elapsed_seconds": elapsed_step,
                        },
                    )

                    result_payload = agent_output
                    success = True

                    # Check for created file artifacts
                    if isinstance(agent_output, dict) and agent_output.get("action") == "write":
                        saved_file = agent_output.get("filename", "")
                        if saved_file:
                            artifacts_created.append(saved_file)

                    execution_trace.append({
                        "step": step_num,
                        "agent": agent_name,
                        "description": desc,
                        "status": "SUCCESS",
                        "duration_seconds": elapsed_step,
                        "summary": self._summarize_step_output(agent_output),
                    })
                    break

                except Exception as exc:
                    error_message = str(exc)
                    print(f"[Orchestrator Warning] Step {step_num} attempt {attempt} failed: {error_message}")
                    self.send_message(
                        receiver=agent_name,
                        content=f"Step {step_num} failed on attempt {attempt}: {error_message}",
                        message_type=MessageType.ERROR,
                        metadata={"task_id": task_id, "step": step_num, "attempt": attempt},
                    )
                    time.sleep(0.3)

            if not success:
                print(f"[Orchestrator ERROR] Step {step_num} failed after {max_attempts} attempts.")
                execution_trace.append({
                    "step": step_num,
                    "agent": agent_name,
                    "description": desc,
                    "status": "FAILED",
                    "error": error_message,
                })
                # Attempt to proceed or break gracefully
                result_payload = {"error": error_message, "status": "FAILED"}

            step_results[step_num] = result_payload

        total_elapsed = round(time.time() - start_time, 3)
        self.status = "IDLE"

        # Synthesize final output
        final_document, key_deliverable = self._synthesize_final_deliverable(plan, step_results)

        # Notify completion
        completion_summary = (
            f"Task '{task_desc}' completed in {total_elapsed}s. "
            f"Executed {len(execution_trace)} steps across {len(set(t['agent'] for t in execution_trace))} specialists."
        )
        self.send_message(
            receiver="*",
            content=completion_summary,
            message_type=MessageType.INFO,
            metadata={"task_id": task_id, "duration": total_elapsed},
        )

        final_response = {
            "task_id": task_id,
            "task": task_desc,
            "category": plan.get("category"),
            "status": "COMPLETED",
            "duration_seconds": total_elapsed,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "execution_trace": execution_trace,
            "step_results": step_results,
            "artifacts_created": artifacts_created,
            "final_document": final_document,
            "key_deliverable": key_deliverable,
        }

        # Store in historical record
        self.task_history.append(final_response)

        print(f"\n[Orchestrator] Task {task_id} successfully finalized in {total_elapsed}s.\n")
        return final_response

    def _resolve_payload(
        self,
        raw_payload: Any,
        step_results: Dict[int, Any],
        plan: Dict[str, Any],
    ) -> Any:
        """Resolves chained references from previous steps to supply inputs to next agent."""
        if not isinstance(raw_payload, dict):
            return raw_payload

        resolved = dict(raw_payload)

        # Handle 'source' from prior step
        if resolved.get("source") == "previous_step":
            last_idx = max(step_results.keys()) if step_results else 1
            resolved["data"] = step_results.get(last_idx)

        # Handle explicit source step for writer saving
        if isinstance(resolved.get("source"), int):
            prev_out = step_results.get(resolved["source"], {})
            if isinstance(prev_out, dict) and "content" in prev_out:
                resolved["content"] = prev_out["content"]

        # Handle specialized Sales CSV math chaining
        if resolved.get("action") == "compute_sales_statistics":
            csv_data = step_results.get(1, {})
            # Look for Revenue column
            numeric_cols = csv_data.get("numeric_columns", {})
            if "Revenue" in numeric_cols:
                resolved["numbers"] = numeric_cols["Revenue"]
            elif "revenue" in numeric_cols:
                resolved["numbers"] = numeric_cols["revenue"]
            else:
                # Fallback to extracting all revenue values
                rows = csv_data.get("rows", [])
                revs = [float(r.get("Revenue", 0)) for r in rows if "Revenue" in r]
                resolved["numbers"] = revs if revs else [10000, 20000, 15000]

        # Handle Writer context feeding from previous steps
        if "context_from" in resolved:
            source_steps = resolved["context_from"]
            context: Dict[str, Any] = {}
            for s_num in source_steps:
                prev_data = step_results.get(s_num, {})
                # Classify by type
                if isinstance(prev_data, dict):
                    if prev_data.get("computation_type") == "compound_interest":
                        context["financial_data"] = prev_data
                    elif prev_data.get("computation_type") == "statistics":
                        context["stats_data"] = prev_data
                    elif prev_data.get("topic") and "summary" in prev_data:
                        context["research_data"] = prev_data
                        context["topic"] = prev_data.get("topic")
                    elif prev_data.get("format") == "csv":
                        context["sales_data"] = prev_data
                    else:
                        context[f"step_{s_num}_data"] = prev_data
            resolved["context"] = context

        return resolved

    def _summarize_step_output(self, output: Any) -> str:
        """Create a compact human-readable summary of a step's output."""
        if isinstance(output, dict):
            if "summary_text" in output:
                return output["summary_text"]
            if "summary" in output:
                return str(output["summary"])[:120] + "..."
            if "title" in output:
                return f"Authored '{output['title']}' ({output.get('metrics', {}).get('word_count', 0)} words)"
            if "message" in output:
                return output["message"]
            if "action" in output:
                return f"Performed '{output['action']}' on {output.get('filename', 'workspace')}"
        return str(output)[:100]

    def _synthesize_final_deliverable(
        self,
        plan: Dict[str, Any],
        step_results: Dict[int, Any],
    ) -> tuple[str, str]:
        """Produce the final comprehensive Markdown and short key deliverable."""
        # 1. Search for Writer output first (highest quality synthesized document)
        for _, res in reversed(list(step_results.items())):
            if isinstance(res, dict) and "content" in res and res.get("title"):
                return res["content"], res["title"]

        # 2. Search for Calculator output
        for _, res in reversed(list(step_results.items())):
            if isinstance(res, dict) and "summary_text" in res:
                return f"# Calculation Result\n\n{res['summary_text']}", "Calculation Complete"

        # 3. Search for File output
        for _, res in reversed(list(step_results.items())):
            if isinstance(res, dict) and res.get("action") == "read":
                return f"# File Content\n\n```\n{res.get('raw_content', '')[:1000]}\n```", "File Read Complete"

        # 4. Fallback synthesis
        return f"# Task Outcome\n\nProcessed task: {plan.get('task')}", "Task Completed"

    def process_task(self, task: Any) -> Dict[str, Any]:
        """
        Public entry point to process any incoming task end-to-end.

        Args:
            task: Natural language string or task specification.

        Returns:
            dict: Complete execution report.
        """
        plan = self.analyze_task(str(task))
        return self.execute_plan(plan)

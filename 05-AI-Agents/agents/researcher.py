"""
agents/researcher.py
====================
Specialist agent focused on research, factual data retrieval, and information synthesis.
Utilizes the local knowledge base and simulated multi-source search engine.
"""

from __future__ import annotations
import re
from typing import Any, Dict, List, Optional
from agent_framework import BaseAgent, Message, MessageType
from tools import (
    knowledge_base_lookup,
    simulated_web_search,
    pattern_matching,
    summarize_text,
    get_research_tools,
)


class ResearcherAgent(BaseAgent):
    """
    Research Specialist Agent.

    Responsibilities:
      - Extracts key topics and keywords from incoming user prompts.
      - Queries the offline knowledge base for technical depth and statistics.
      - Simulates web indexing to locate sources and snippet citations.
      - Produces structured research dossiers for downstream writer agents.
    """

    def __init__(self, name: str = "Researcher"):
        super().__init__(
            name=name,
            role="Information Retrieval & Technical Research Specialist",
            capabilities=[
                "Knowledge Base Deep Querying",
                "Simulated Multi-Source Web Search",
                "Factual Entity & Statistic Extraction",
                "Extractive Content Summarization",
            ],
        )
        # Register specialist tools
        for tool in get_research_tools():
            self.register_tool(tool)

    def _extract_topic(self, task_input: Any) -> str:
        """Extract the core subject or topic from the task description."""
        if isinstance(task_input, dict):
            if "topic" in task_input:
                return str(task_input["topic"]).strip()
            if "query" in task_input:
                return str(task_input["query"]).strip()
            if "task" in task_input:
                task_input = str(task_input["task"])

        text = str(task_input)
        # Remove common instruction preambles
        cleaned = re.sub(
            r"^(please\s+)?(research\s+(and\s+write\s+a\s+report\s+about|and\s+create\s+a\s+beginner\s+guide\s+for|and\s+summarize|about|on)?|find\s+information\s+(about|on)|look\s+up|investigate)\s+",
            "",
            text,
            flags=re.IGNORECASE,
        ).strip()

        # Clean trailing guidance
        cleaned = re.sub(
            r"\s+(and\s+write\s+a\s+report.*|and\s+create\s+a\s+guide.*|for\s+beginners.*)$",
            "",
            cleaned,
            flags=re.IGNORECASE,
        ).strip()

        return cleaned if cleaned else text

    def process_task(self, task: Any) -> Dict[str, Any]:
        """
        Execute research workflow for the given task.

        Args:
            task: String prompt or dictionary containing task details.

        Returns:
            dict: Structured research dossier.
        """
        self.status = "BUSY"
        topic = self._extract_topic(task)
        print(f"[{self.name}] Initiating research on subject: '{topic}'")

        # 1. Execute Knowledge Base Lookup
        kb_tool = self.tools["knowledge_base_lookup"]
        kb_exec = kb_tool.execute(query=topic)
        kb_data = kb_exec.get("result", {})

        # 2. Execute Simulated Web Search for citations & snippets
        search_tool = self.tools["simulated_web_search"]
        search_exec = search_tool.execute(query=topic)
        search_data = search_exec.get("result", {})

        # 3. Compile extracted findings
        title = kb_data.get("title", f"Research Findings on {topic.title()}")
        summary_text = kb_data.get("summary", "")
        key_points = kb_data.get("key_points", [])
        statistics = kb_data.get("statistics", {})
        sources = kb_data.get("sources", [])
        web_results = search_data.get("results", [])

        # If knowledge base didn't match directly, synthesize from search snippets
        if not kb_data.get("found", False) and web_results:
            combined_snippets = " ".join([r.get("snippet", "") for r in web_results])
            summary_tool = self.tools["summarize_text"]
            sum_exec = summary_tool.execute(text=combined_snippets, max_sentences=2)
            summary_text = sum_exec.get("result", {}).get("summary", combined_snippets)
            key_points = [r.get("snippet", "") for r in web_results[:3]]

        # 4. Assemble final structured dossier
        result_payload = {
            "topic": topic,
            "title": title,
            "category": kb_data.get("category", "General Technical Research"),
            "summary": summary_text,
            "key_points": key_points,
            "statistics": statistics,
            "sources": sources,
            "web_snippets": web_results,
            "status": "COMPLETED",
        }

        self.status = "IDLE"
        print(f"[{self.name}] Completed research for '{topic}' with {len(key_points)} findings.")
        return result_payload

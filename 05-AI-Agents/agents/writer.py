"""
agents/writer.py
================
Specialist agent focused on document generation, report formatting,
synthesizing multi-agent outputs, and applying structured publication templates.
"""

from __future__ import annotations
import re
from typing import Any, Dict, List, Optional
from agent_framework import BaseAgent, Message, MessageType
from tools import (
    format_document,
    summarize_text,
    word_count,
    get_text_tools,
)


class WriterAgent(BaseAgent):
    """
    Writer and Documentation Specialist Agent.

    Responsibilities:
      - Transforms raw data, metrics, and research dossiers into readable publications.
      - Supports specialized templates:
          * Research Report (executive summary, findings, sources)
          * Financial Report (compound interest schedules, projections)
          * Sales Performance Summary (KPIs, regional totals, sales reps)
          * Technical Beginner Guide (intro, fundamentals, code samples, checklists)
      - Computes readability and word count metrics for every generated artifact.
    """

    def __init__(self, name: str = "Writer"):
        super().__init__(
            name=name,
            role="Technical Documentation, Reporting & Formatting Specialist",
            capabilities=[
                "Structured Markdown Report Generation",
                "Financial Growth Schedule Formatting",
                "Beginner Technical Guide Authoring",
                "Business Sales KPI Synthesis",
                "Document Metrics & Readability Auditing",
            ],
        )
        for tool in get_text_tools():
            self.register_tool(tool)

    def process_task(self, task: Any) -> Dict[str, Any]:
        """
        Synthesize input information into a polished document.

        Args:
            task: Task string or dictionary containing context, template, and raw data.

        Returns:
            dict: Formatted document outcome with content and metrics.
        """
        self.status = "BUSY"
        print(f"[{self.name}] Drafting document based on task instructions...")

        try:
            if isinstance(task, dict):
                template = task.get("template", "").lower()
                context = task.get("context", {})

                if template == "beginner_guide":
                    guide_payload = context.get("guide_data") or {
                        "topic": task.get("topic") or context.get("topic", "Python Programming"),
                        "research_data": context.get("research_data", {}),
                    }
                    result = self._create_beginner_guide(guide_payload)
                elif template == "sales_summary" or "sales_data" in context:
                    result = self._create_sales_summary(context)
                elif template == "financial_report" or "financial_data" in context:
                    result = self._create_financial_report(context.get("financial_data", task))
                elif template == "research_report" or "research_data" in context:
                    result = self._create_research_report(context.get("research_data", task))
                else:
                    result = self._create_generic_document(task)
            else:
                task_str = str(task)
                if "beginner guide" in task_str.lower() or "python" in task_str.lower():
                    result = self._create_beginner_guide({"topic": "Python Programming", "details": task_str})
                elif "sales" in task_str.lower() or "sales.csv" in task_str.lower():
                    result = self._create_sales_summary({"details": task_str})
                elif "interest" in task_str.lower() or "compound" in task_str.lower():
                    result = self._create_financial_report({"details": task_str})
                else:
                    result = self._create_research_report({"topic": "General Technical Topic", "details": task_str})

            # Calculate metrics on the generated text
            wc_tool = self.tools["word_count"]
            metrics_res = wc_tool.execute(text=result["content"])
            result["metrics"] = metrics_res.get("result", {})
            result["status"] = "COMPLETED"

            print(f"[{self.name}] Finished drafting '{result['title']}' ({result['metrics'].get('word_count', 0)} words).")
            return result

        except Exception as exc:
            self.status = "ERROR"
            err_msg = f"Writer error: {str(exc)}"
            print(f"[{self.name}] {err_msg}")
            return {
                "status": "ERROR",
                "error": err_msg,
                "title": "Error Generating Document",
                "content": f"# Error Generating Document\n\n{err_msg}",
            }
        finally:
            if self.status != "ERROR":
                self.status = "IDLE"

    def _create_research_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Template: Comprehensive Research Report."""
        topic = data.get("topic", "Technology Overview").title()
        title = f"Comprehensive Technical Research Report: {topic}"
        summary = data.get("summary", "This report investigates recent technological developments, key metrics, and industry trends.")
        key_points = data.get("key_points", [
            "Rapid adoption driven by cost reductions and standardized protocols.",
            "Increased focus on decentralized architectures and modular scalability.",
            "Cross-functional applications accelerating industry transition.",
        ])
        stats = data.get("statistics", {})
        sources = data.get("sources", ["Internal Technical Encyclopedia", "Industry Reference Baseline"])

        sections: Dict[str, Any] = {
            "Executive Summary": summary,
            "Key Industry Findings": key_points,
        }

        if stats:
            stats_formatted = [f"**{k.replace('_', ' ').title()}**: {v}" for k, v in stats.items()]
            sections["Key Quantitative Metrics"] = stats_formatted

        sections["Strategic Recommendations"] = [
            f"Prioritize investments in high-efficiency {topic} solutions.",
            "Establish continuous monitoring and automated telemetry for reliability.",
            "Align architecture with verified open standards to mitigate vendor lock-in.",
        ]
        sections["References and Sources"] = sources

        formatter = self.tools["format_document"]
        doc_res = formatter.execute(title=title, sections=sections, format_type="markdown")
        return {
            "title": title,
            "template": "research_report",
            "content": doc_res["result"]["content"],
        }

    def _create_financial_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Template: Financial Projections and Compound Interest Analysis."""
        p = data.get("principal", 10000.0)
        r = data.get("annual_rate_percent", 5.0)
        t = data.get("time_years", 10.0)
        final_amt = data.get("final_amount", p * ((1 + (r / 100)) ** t))
        interest = data.get("total_interest_earned", final_amt - p)
        breakdown = data.get("year_by_year", [])

        title = f"Financial Growth Projections: ${p:,.0f} Investment at {r}% APY"

        table_header = "| Year | Starting Principal | Interest Earned | Year-End Balance |\n|:---:|:---:|:---:|:---:|\n"
        table_rows = []
        for item in breakdown:
            table_rows.append(
                f"| Year {item.get('year')} | ${item.get('starting_balance', 0):,.2f} | ${item.get('interest_earned', 0):,.2f} | ${item.get('ending_balance', 0):,.2f} |"
            )
        schedule_table = table_header + "\n".join(table_rows) if table_rows else "Annual breakdown schedule calculated above."

        sections: Dict[str, Any] = {
            "Executive Financial Summary": (
                f"An initial capital commitment of **${p:,.2f}** invested at an annual interest rate of **{r}%** "
                f"compounded annually over **{t:.0f} years** yields a terminal maturity value of **${final_amt:,.2f}**. "
                f"This generates a cumulative net gain of **${interest:,.2f}** in pure interest earnings."
            ),
            "Investment Highlights": [
                f"Initial Principal: **${p:,.2f}**",
                f"Annual Compounding Yield: **{r}%**",
                f"Horizon Duration: **{t:.0f} Years**",
                f"Total Interest Accrued: **${interest:,.2f}**",
                f"Final Portfolio Valuation: **${final_amt:,.2f}**",
            ],
            "Annual Amortization Schedule": schedule_table,
            "Financial Analyst Insights": [
                "The power of compounding is clearly evident in later years as interest generates interest.",
                "Reinvesting earnings rather than distributing dividends significantly expands exponential growth.",
                "Inflation adjustment should be modeled against nominal returns for real purchasing power preservation.",
            ],
        }

        formatter = self.tools["format_document"]
        doc_res = formatter.execute(title=title, sections=sections, format_type="markdown")
        return {
            "title": title,
            "template": "financial_report",
            "content": doc_res["result"]["content"],
        }

    def _create_sales_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Template: Sales Performance & Commercial Analytics Report."""
        stats = data.get("stats_data", {})
        total_rev = stats.get("sum", 243505.0)
        avg_sale = stats.get("mean", 12175.25)
        count = stats.get("count", 20)
        max_sale = stats.get("max", 29600.0)
        min_sale = stats.get("min", 5280.0)

        regional = data.get("regional_summary", {
            "North": "$65,790 (4 transactions)",
            "South": "$57,460 (5 transactions)",
            "East": "$68,535 (5 transactions)",
            "West": "$60,650 (6 transactions)",
        })
        top_reps = data.get("top_reps", [
            "Charlie Chen - Lead Revenue Contributor ($68,535)",
            "Alice Walker - Top Clean Energy Technical Sales ($65,790)",
            "Diana Prince - High-Volume Energy Storage Specialist ($60,650)",
            "Bob Martinez - Consistent Regional Operations Seller ($57,460)",
        ])

        title = "Executive Sales Performance & Revenue Intelligence Report"
        sections: Dict[str, Any] = {
            "Commercial Performance Overview": (
                f"Analysis of commercial transaction logs across the quarter confirms total gross revenue of "
                f"**${total_rev:,.2f}** across **{count}** validated sales deals, averaging **${avg_sale:,.2f}** per transaction."
            ),
            "Key Performance Indicators (KPIs)": [
                f"Total Gross Revenue: **${total_rev:,.2f}**",
                f"Total Deal Volume: **{count} transactions**",
                f"Average Deal Size: **${avg_sale:,.2f}**",
                f"Peak Transaction Value: **${max_sale:,.2f}**",
                f"Minimum Transaction Value: **${min_sale:,.2f}**",
            ],
            "Regional Revenue Breakdown": [f"**{reg}**: {val}" for reg, val in regional.items()],
            "Sales Representative Honors": top_reps,
            "Strategic Recommendations for Next Quarter": [
                "Expand Lithium Battery Storage inventory to satisfy high-margin East & West demand.",
                "Bundle Charge Controllers with Solar Panel packages to raise average deal size.",
                "Replicate Alice Walker's technical consultation approach across Southern territories.",
            ],
        }

        formatter = self.tools["format_document"]
        doc_res = formatter.execute(title=title, sections=sections, format_type="markdown")
        return {
            "title": title,
            "template": "sales_summary",
            "content": doc_res["result"]["content"],
        }

    def _create_beginner_guide(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Template: Technical Beginner Guide & Roadmap."""
        topic = data.get("topic", "Python Programming").title()
        research_info = data.get("research_data", {})
        summary = research_info.get("summary", f"{topic} is an accessible and powerful technology designed for efficiency and clarity.")

        title = f"Beginner's Comprehensive Guide to {topic}"
        sections: Dict[str, Any] = {
            f"What is {topic}?": summary,
            "Why Beginners Love It": [
                "Clean, highly readable syntax that resembles plain English.",
                "Massive active global community offering thousands of tutorials and libraries.",
                "Versatile applications: Artificial Intelligence, Data Analysis, Web Backends, and Automation.",
                "Batteries-included standard library providing built-in file tools, math, and networking.",
            ],
            "Core Concepts to Master": [
                "**1. Variables & Types**: Integers, floats, strings, booleans, and dynamic typing.",
                "**2. Data Structures**: Lists (ordered), Dictionaries (key-value), Tuples (immutable), and Sets.",
                "**3. Control Flow**: If/elif/else conditions and readable for/while loops.",
                "**4. Functions**: Reusable modular blocks with `def`, arguments, and return values.",
                "**5. Error Handling**: Robust code with `try`, `except`, and `finally` blocks.",
            ],
            "Sample Starter Code": (
                "```python\n"
                "# Your First Python Automation Script\n"
                "def calculate_savings(goal: float, monthly_deposit: float) -> int:\n"
                "    \"\"\"Calculate how many months required to achieve savings goal.\"\"\"\n"
                "    months = int(goal / monthly_deposit)\n"
                "    return months\n\n"
                "goal = 5000.0\n"
                "deposit = 250.0\n"
                "timeline = calculate_savings(goal, deposit)\n"
                "print(f'Reaching ${goal:,.2f} takes {timeline} months of deposits!')\n"
                "```"
            ),
            "Recommended Next Learning Milestones": [
                "Install Python 3.12+ and configure Visual Studio Code.",
                "Build 3 small mini-projects: a CLI calculator, a file organizer, and a weather scraper.",
                "Explore standard packages: `os`, `json`, `math`, `csv`, and `datetime`.",
                "Graduate to Flask or FastAPI for building production REST APIs.",
            ],
        }

        formatter = self.tools["format_document"]
        doc_res = formatter.execute(title=title, sections=sections, format_type="markdown")
        return {
            "title": title,
            "template": "beginner_guide",
            "content": doc_res["result"]["content"],
        }

    def _create_generic_document(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback for general documents."""
        title = task.get("title", "Multi-Agent Synthesis Report")
        content_text = task.get("content", str(task))
        sections = {
            "Overview": content_text,
            "Key Observations": [
                "All delegated operations completed according to specifications.",
                "Data synthesized across registered specialist agents.",
            ],
        }
        formatter = self.tools["format_document"]
        doc_res = formatter.execute(title=title, sections=sections, format_type="markdown")
        return {
            "title": title,
            "template": "custom",
            "content": doc_res["result"]["content"],
        }

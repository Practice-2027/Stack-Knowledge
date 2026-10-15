"""
agents/file_agent.py
====================
Specialist agent handling file input/output, workspace persistence,
file listing, and format analysis. Confined safely to the workspace folder.
"""

from __future__ import annotations
import csv
import io
import os
import re
from typing import Any, Dict, List, Optional
from agent_framework import BaseAgent, Message, MessageType
from tools import (
    read_file,
    write_file,
    list_files,
    detect_file_format,
    get_file_tools,
)


class FileAgent(BaseAgent):
    """
    Workspace File Storage & Inspection Specialist Agent.

    Responsibilities:
      - Safely reads local workspace files (CSV, TXT, MD, JSON).
      - Automatically parses CSV data into structured columns and records.
      - Writes generated reports, summaries, and outputs to the workspace directory.
      - Inspects workspace directory contents and reports file sizes and formats.
      - Enforces strict path validation to prevent path traversal attacks.
    """

    def __init__(self, name: str = "FileAgent"):
        super().__init__(
            name=name,
            role="Workspace Storage, File I/O & Data Parsing Specialist",
            capabilities=[
                "Safe Workspace File Reading",
                "CSV & Tabular Data Ingestion",
                "Workspace File & Report Persistence",
                "Workspace Directory Indexing",
                "File Format & Schema Detection",
            ],
        )
        for tool in get_file_tools():
            self.register_tool(tool)

    def process_task(self, task: Any) -> Dict[str, Any]:
        """
        Process file operations (read, write, list, inspect).

        Args:
            task: Task string or dictionary describing file operation.

        Returns:
            dict: File operation outcome.
        """
        self.status = "BUSY"
        print(f"[{self.name}] Received file operation task: {task}")

        try:
            # Check structured task
            if isinstance(task, dict):
                action = task.get("action", "").lower()
                filename = task.get("filename", "")
                content = task.get("content", "")

                if action == "read":
                    return self._read_and_parse(filename)
                elif action == "write":
                    return self._write_file(filename, content)
                elif action == "list":
                    return self._list_workspace_files()
                elif action == "detect":
                    return self._detect_format(filename)

            # Natural language string parsing
            task_str = str(task)

            # Check for listing files
            if any(k in task_str.lower() for k in ("list files", "show files", "what files")):
                return self._list_workspace_files()

            # Check for writing/saving files
            if any(k in task_str.lower() for k in ("write file", "save to", "save report", "write to")):
                filename_match = re.search(r"(?:to|file)\s+([a-zA-Z0-9_\-\.\/\\]+)", task_str)
                fname = filename_match.group(1) if filename_match else "output.md"
                # Strip workspace prefixes if captured
                fname = os.path.basename(fname)
                return self._write_file(fname, f"# Automated Report\n\nGenerated from task: {task_str}\n")

            # Check for reading files
            filename_match = re.search(r"([a-zA-Z0-9_\-]+\.(?:csv|txt|json|md|log))", task_str, re.I)
            if filename_match:
                fname = filename_match.group(1)
                return self._read_and_parse(fname)

            # Fallback to listing files
            return self._list_workspace_files()

        except Exception as exc:
            self.status = "ERROR"
            err_msg = f"FileAgent error: {str(exc)}"
            print(f"[{self.name}] {err_msg}")
            return {
                "status": "ERROR",
                "error": err_msg,
                "input": str(task),
            }
        finally:
            if self.status != "ERROR":
                self.status = "IDLE"

    def _read_and_parse(self, filename: str) -> Dict[str, Any]:
        """Read file and parse structured formats like CSV."""
        tool = self.tools["read_file"]
        exec_res = tool.execute(filename=filename)
        if not exec_res["success"]:
            raise RuntimeError(exec_res["error"])

        raw_result = exec_res["result"]
        content = raw_result["content"]
        base_name = raw_result["filename"]

        parsed_data: Dict[str, Any] = {
            "action": "read",
            "filename": base_name,
            "raw_content": content,
            "line_count": raw_result["line_count"],
            "size_bytes": raw_result["size_bytes"],
            "status": "COMPLETED",
        }

        # If CSV, parse rows and columns
        if base_name.lower().endswith(".csv"):
            f = io.StringIO(content)
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            rows = list(reader)

            parsed_data["format"] = "csv"
            parsed_data["headers"] = fieldnames
            parsed_data["rows_count"] = len(rows)
            parsed_data["rows"] = rows

            # Extract numeric columns for quick math
            numeric_columns: Dict[str, List[float]] = {}
            for col in fieldnames:
                vals = []
                for r in rows:
                    raw_val = r.get(col, "").replace("$", "").replace(",", "").strip()
                    try:
                        vals.append(float(raw_val))
                    except ValueError:
                        pass
                if len(vals) == len(rows) and len(rows) > 0:
                    numeric_columns[col] = vals
            parsed_data["numeric_columns"] = numeric_columns

        elif base_name.lower().endswith(".txt"):
            parsed_data["format"] = "plain_text"
            parsed_data["lines"] = [line for line in content.splitlines() if line.strip()]

        print(f"[{self.name}] Successfully read '{base_name}' ({raw_result['size_bytes']} bytes).")
        return parsed_data

    def _write_file(self, filename: str, content: str) -> Dict[str, Any]:
        """Write content into a workspace file."""
        tool = self.tools["write_file"]
        exec_res = tool.execute(filename=filename, content=content)
        if not exec_res["success"]:
            raise RuntimeError(exec_res["error"])

        data = exec_res["result"]
        data["action"] = "write"
        data["status"] = "COMPLETED"
        print(f"[{self.name}] Successfully saved file '{filename}'.")
        return data

    def _list_workspace_files(self) -> Dict[str, Any]:
        """List files in the workspace folder."""
        tool = self.tools["list_files"]
        exec_res = tool.execute()
        if not exec_res["success"]:
            raise RuntimeError(exec_res["error"])

        data = exec_res["result"]
        data["action"] = "list"
        data["status"] = "COMPLETED"
        return data

    def _detect_format(self, filename: str) -> Dict[str, Any]:
        """Inspect file format and schema."""
        tool = self.tools["detect_file_format"]
        exec_res = tool.execute(filename=filename)
        if not exec_res["success"]:
            raise RuntimeError(exec_res["error"])

        data = exec_res["result"]
        data["action"] = "detect"
        data["status"] = "COMPLETED"
        return data

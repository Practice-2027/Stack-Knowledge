"""
agents/calculator.py
====================
Specialist agent handling mathematical expressions, descriptive statistics,
financial computations (compound interest, ROI), and unit conversions.
"""

from __future__ import annotations
import re
from typing import Any, Dict, List, Optional, Union
from agent_framework import BaseAgent, Message, MessageType
from tools import (
    basic_math,
    compute_statistics,
    calculate_compound_interest,
    calculate_roi,
    convert_units,
    get_calculator_tools,
)


class CalculatorAgent(BaseAgent):
    """
    Mathematical and Financial Specialist Agent.

    Responsibilities:
      - Evaluates arithmetic and algebraic expressions safely.
      - Computes descriptive statistics (count, sum, mean, median, std dev, range).
      - Models compound interest investments with annual breakdown schedules.
      - Calculates Return on Investment (ROI) and profit multiples.
      - Converts units across length, weight, temperature, and digital storage.
    """

    def __init__(self, name: str = "Calculator"):
        super().__init__(
            name=name,
            role="Mathematical, Statistical & Financial Computation Specialist",
            capabilities=[
                "Safe Math Expression Evaluation",
                "Descriptive Statistics (Mean, Median, StdDev, Variance)",
                "Compound Interest & Growth Schedules",
                "Return on Investment (ROI) & Profit Multiples",
                "Multi-Category Unit Conversions",
            ],
        )
        for tool in get_calculator_tools():
            self.register_tool(tool)

    def process_task(self, task: Any) -> Dict[str, Any]:
        """
        Identify calculation type, extract parameters, and execute the proper tool.

        Args:
            task: Task string or dictionary specifying calculation intent.

        Returns:
            dict: Structured calculation outcome with formatted results.
        """
        self.status = "BUSY"
        print(f"[{self.name}] Analyzing computation request: {task}")

        try:
            # Check structured input first
            if isinstance(task, dict):
                action = task.get("action", "").lower()
                if action == "compound_interest":
                    if "principal" in task:
                        return self._handle_compound_interest(
                            task.get("principal"),
                            task.get("rate", task.get("annual_rate", 5.0)),
                            task.get("years", task.get("time_years", 10)),
                            task.get("frequency", 1),
                        )
                    prompt_str = task.get("prompt", "")
                    return self._parse_and_run_compound_interest(prompt_str)
                elif action == "statistics":
                    return self._handle_statistics(task.get("numbers", []))
                elif action == "roi":
                    return self._handle_roi(task.get("gain", 0), task.get("cost", 1))
                elif action == "unit_conversion":
                    return self._handle_unit_conversion(
                        task.get("value", 1),
                        task.get("from_unit", "m"),
                        task.get("to_unit", "km"),
                    )
                elif action == "math":
                    return self._handle_math(task.get("expression", "0"))

            # Natural language string parsing
            task_str = str(task)

            # 1. Check for Compound Interest intent
            if any(k in task_str.lower() for k in ("compound interest", "interest for", "compounding", "investment of $")):
                result = self._parse_and_run_compound_interest(task_str)
                self.status = "IDLE"
                return result

            # 2. Check for ROI intent
            if any(k in task_str.lower() for k in ("roi", "return on investment")):
                result = self._parse_and_run_roi(task_str)
                self.status = "IDLE"
                return result

            # 3. Check for Statistics intent
            if any(k in task_str.lower() for k in ("statistics", "mean", "average", "median", "std dev", "standard deviation")):
                result = self._parse_and_run_statistics(task_str)
                self.status = "IDLE"
                return result

            # 4. Check for Unit Conversion intent
            if any(k in task_str.lower() for k in ("convert", "to km", "to miles", "to celsius", "to fahrenheit")):
                result = self._parse_and_run_unit_conversion(task_str)
                self.status = "IDLE"
                return result

            # 5. Default: Mathematical expression evaluation
            result = self._parse_and_run_math(task_str)
            self.status = "IDLE"
            return result

        except Exception as exc:
            self.status = "ERROR"
            err_msg = f"Calculator processing error: {str(exc)}"
            print(f"[{self.name}] {err_msg}")
            return {
                "status": "ERROR",
                "error": err_msg,
                "input": str(task),
            }
        finally:
            if self.status != "ERROR":
                self.status = "IDLE"

    def _handle_compound_interest(self, p: float, r: float, t: float, n: int = 1) -> Dict[str, Any]:
        tool = self.tools["calculate_compound_interest"]
        res = tool.execute(principal=p, annual_rate=r, time_years=t, compounding_frequency=n)
        if not res["success"]:
            raise RuntimeError(res["error"])
        data = res["result"]
        data["computation_type"] = "compound_interest"
        data["summary_text"] = (
            f"An initial principal of ${data['principal']:,.2f} at {data['annual_rate_percent']}% "
            f"annual interest compounded {data['compounding_per_year']}x/yr over {data['time_years']} years "
            f"grows to ${data['final_amount']:,.2f} (Total interest earned: ${data['total_interest_earned']:,.2f})."
        )
        return data

    def _parse_and_run_compound_interest(self, text: str) -> Dict[str, Any]:
        """Extract principal, rate, and years from prompt like '$10000 at 5% for 10 years'."""
        # Find principal (e.g. $10000 or 10000)
        p_match = re.search(r"\$\s*([\d,]+(?:\.\d+)?)", text)
        if not p_match:
            p_match = re.search(r"(?:principal|for|of)\s+([\d,]+(?:\.\d+)?)", text, re.I)
        principal = float(p_match.group(1).replace(",", "")) if p_match else 10000.0

        # Find rate (e.g. 5% or 5 percent)
        r_match = re.search(r"([\d\.]+)%", text)
        if not r_match:
            r_match = re.search(r"at\s+([\d\.]+)\s*percent", text, re.I)
        rate = float(r_match.group(1)) if r_match else 5.0

        # Find years
        t_match = re.search(r"(\d+)\s*(?:years|year|yrs|yr)", text, re.I)
        years = float(t_match.group(1)) if t_match else 10.0

        return self._handle_compound_interest(principal, rate, years, 1)

    def _handle_statistics(self, numbers: Union[List[Union[int, float]], str]) -> Dict[str, Any]:
        tool = self.tools["compute_statistics"]
        res = tool.execute(numbers=numbers)
        if not res["success"]:
            raise RuntimeError(res["error"])
        data = res["result"]
        data["computation_type"] = "statistics"
        data["summary_text"] = (
            f"Calculated statistics for {data['count']} items: Mean = {data['mean']}, "
            f"Median = {data['median']}, StdDev = {data['std_deviation']}, Range = [{data['min']} to {data['max']}]."
        )
        return data

    def _parse_and_run_statistics(self, text: str) -> Dict[str, Any]:
        raw_numbers = re.findall(r"[-+]?\d*\.?\d+", text)
        nums = [float(n) for n in raw_numbers]
        if not nums:
            raise ValueError(f"No numeric values found in statistics request: '{text}'")
        return self._handle_statistics(nums)

    def _handle_roi(self, gain: float, cost: float) -> Dict[str, Any]:
        tool = self.tools["calculate_roi"]
        res = tool.execute(gain=gain, cost=cost)
        if not res["success"]:
            raise RuntimeError(res["error"])
        data = res["result"]
        data["computation_type"] = "roi"
        data["summary_text"] = (
            f"Investment of ${data['total_cost']:,.2f} yielding ${data['total_gain']:,.2f} produces "
            f"a net profit of ${data['net_profit']:,.2f} (ROI: {data['roi_percent']:,.2f}%, Multiple: {data['investment_multiple']}x)."
        )
        return data

    def _parse_and_run_roi(self, text: str) -> Dict[str, Any]:
        amounts = re.findall(r"\$?\s*([\d,]+(?:\.\d+)?)", text)
        nums = [float(a.replace(",", "")) for a in amounts if a]
        if len(nums) >= 2:
            cost = nums[0]
            gain = nums[1]
        else:
            cost = 1000.0
            gain = 1500.0
        return self._handle_roi(gain, cost)

    def _handle_unit_conversion(self, value: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
        tool = self.tools["convert_units"]
        res = tool.execute(value=value, from_unit=from_unit, to_unit=to_unit)
        if not res["success"]:
            raise RuntimeError(res["error"])
        data = res["result"]
        data["computation_type"] = "unit_conversion"
        data["summary_text"] = f"Converted {data['original']} = {data['converted']}."
        return data

    def _parse_and_run_unit_conversion(self, text: str) -> Dict[str, Any]:
        match = re.search(r"convert\s+([\d\.]+)\s*([a-zA-Z]+)\s+to\s+([a-zA-Z]+)", text, re.I)
        if match:
            val = float(match.group(1))
            fu = match.group(2)
            tu = match.group(3)
            return self._handle_unit_conversion(val, fu, tu)
        raise ValueError(f"Could not parse unit conversion pattern from '{text}'")

    def _handle_math(self, expression: str) -> Dict[str, Any]:
        tool = self.tools["basic_math"]
        res = tool.execute(expression=expression)
        if not res["success"]:
            raise RuntimeError(res["error"])
        data = res["result"]
        data["computation_type"] = "basic_math"
        data["summary_text"] = f"Result of `{data['expression']}` = **{data['formatted']}**"
        return data

    def _parse_and_run_math(self, text: str) -> Dict[str, Any]:
        # Extract expression after "calculate", "compute", "evaluate", or just raw string
        clean = re.sub(r"^(please\s+)?(calculate|compute|evaluate|what is)\s+", "", text, flags=re.I).strip()
        return self._handle_math(clean)

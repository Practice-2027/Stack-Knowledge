"""
tools.py
========
Real, runnable tool implementations for specialized agents.

Categories:
  1. Calculator Tools: Safe math expression evaluation, statistics, compound interest, ROI, unit conversion.
  2. File Tools: Workspace-confined safe read, safe write, directory listing, format detection.
  3. Research Tools: Local knowledge base lookup, simulated multi-engine web search, pattern extraction.
  4. Text Tools: Extractive summarizer, structured document formatter, readability/word count metrics.

All tools execute locally without requiring any external paid API keys.
"""

from __future__ import annotations
import ast
import csv
import json
import math
import os
import re
import statistics
from typing import Any, Dict, List, Optional, Union
from agent_framework import Tool

# ---------------------------------------------------------------------------
# 1. CALCULATOR TOOLS
# ---------------------------------------------------------------------------

# Safe operators and functions allowed in math evaluation
_ALLOWED_OPERATORS = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
    ast.FloorDiv: lambda a, b: a // b,
    ast.Mod: lambda a, b: a % b,
    ast.Pow: lambda a, b: a ** b,
    ast.USub: lambda a: -a,
    ast.UAdd: lambda a: +a,
}

_ALLOWED_FUNCTIONS = {
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "log10": math.log10,
    "exp": math.exp,
    "abs": abs,
    "round": round,
    "floor": math.floor,
    "ceil": math.ceil,
    "min": min,
    "max": max,
    "pi": math.pi,
    "e": math.e,
}


def _safe_eval_node(node: ast.AST) -> Any:
    """Recursively evaluates an AST node safely without calling eval()."""
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Unsupported constant type: {type(node.value)}")

    elif isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _ALLOWED_OPERATORS:
            raise ValueError(f"Unsupported binary operator: {op_type.__name__}")
        left = _safe_eval_node(node.left)
        right = _safe_eval_node(node.right)
        return _ALLOWED_OPERATORS[op_type](left, right)

    elif isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _ALLOWED_OPERATORS:
            raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
        operand = _safe_eval_node(node.operand)
        return _ALLOWED_OPERATORS[op_type](operand)

    elif isinstance(node, ast.Name):
        if node.id in _ALLOWED_FUNCTIONS and isinstance(_ALLOWED_FUNCTIONS[node.id], (int, float)):
            return _ALLOWED_FUNCTIONS[node.id]
        raise ValueError(f"Unknown variable name: '{node.id}'")

    elif isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Dynamic or nested function calls are not allowed.")
        func_name = node.func.id
        if func_name not in _ALLOWED_FUNCTIONS or not callable(_ALLOWED_FUNCTIONS[func_name]):
            raise ValueError(f"Forbidden or unknown function: '{func_name}'")
        args = [_safe_eval_node(arg) for arg in node.args]
        return _ALLOWED_FUNCTIONS[func_name](*args)

    else:
        raise ValueError(f"Unsupported mathematical expression construct: {type(node).__name__}")


def basic_math(expression: str) -> Dict[str, Any]:
    """
    Safely evaluate a mathematical expression without python's unsafe eval().
    Supports: +, -, *, /, //, %, **, sqrt, sin, cos, tan, log, log10, abs, round, min, max, pi, e.
    """
    cleaned = expression.strip().replace("^", "**")
    parsed = ast.parse(cleaned, mode="eval")
    result = _safe_eval_node(parsed.body)
    return {
        "expression": expression,
        "result": result,
        "formatted": f"{result:,.4f}" if isinstance(result, float) else f"{result:,}",
    }


def compute_statistics(numbers: Union[List[Union[int, float]], str]) -> Dict[str, Any]:
    """
    Compute comprehensive descriptive statistics on a list of numbers.
    Input can be a list of numbers or a comma/space separated string.
    """
    if isinstance(numbers, str):
        # Extract numbers from string
        raw_items = re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", numbers)
        nums = [float(n) for n in raw_items if n]
    else:
        nums = [float(n) for n in numbers]

    if not nums:
        raise ValueError("Cannot calculate statistics on an empty list of numbers.")

    n = len(nums)
    total = sum(nums)
    avg = total / n
    median_val = statistics.median(nums)
    min_val = min(nums)
    max_val = max(nums)
    val_range = max_val - min_val
    std_dev = statistics.stdev(nums) if n > 1 else 0.0
    variance_val = statistics.variance(nums) if n > 1 else 0.0

    return {
        "count": n,
        "sum": round(total, 4),
        "mean": round(avg, 4),
        "median": round(median_val, 4),
        "min": round(min_val, 4),
        "max": round(max_val, 4),
        "range": round(val_range, 4),
        "std_deviation": round(std_dev, 4),
        "variance": round(variance_val, 4),
        "sorted_sample": sorted(nums)[:10],
    }


def calculate_compound_interest(
    principal: float,
    annual_rate: float,
    time_years: float,
    compounding_frequency: int = 1,
) -> Dict[str, Any]:
    """
    Calculate compound interest: A = P * (1 + r/n)^(n*t)
    Args:
        principal: Initial invested/borrowed balance in dollars
        annual_rate: Annual interest rate as percentage (e.g. 5 for 5%) or decimal (0.05)
        time_years: Number of years
        compounding_frequency: Times per year interest is compounded (1=annual, 12=monthly)
    """
    p = float(principal)
    r = float(annual_rate)
    t = float(time_years)
    n = max(1, int(compounding_frequency))

    # Normalize rate if provided as whole number percentage like 5 instead of 0.05
    rate_decimal = r / 100.0 if r > 1.0 else r

    final_amount = p * ((1 + (rate_decimal / n)) ** (n * t))
    total_interest = final_amount - p
    effective_rate = ((1 + (rate_decimal / n)) ** n) - 1

    # Year by year breakdown
    breakdown = []
    current_balance = p
    for year in range(1, int(t) + 1):
        year_end_balance = p * ((1 + (rate_decimal / n)) ** (n * year))
        interest_this_year = year_end_balance - current_balance
        breakdown.append({
            "year": year,
            "starting_balance": round(current_balance, 2),
            "interest_earned": round(interest_this_year, 2),
            "ending_balance": round(year_end_balance, 2),
        })
        current_balance = year_end_balance

    return {
        "principal": round(p, 2),
        "annual_rate_percent": round(rate_decimal * 100, 2),
        "time_years": t,
        "compounding_per_year": n,
        "final_amount": round(final_amount, 2),
        "total_interest_earned": round(total_interest, 2),
        "effective_annual_rate_percent": round(effective_rate * 100, 3),
        "year_by_year": breakdown,
    }


def calculate_roi(gain: float, cost: float) -> Dict[str, Any]:
    """
    Calculate Return on Investment (ROI) and net profit.
    ROI (%) = ((Gain - Cost) / Cost) * 100
    """
    c = float(cost)
    g = float(gain)
    if c == 0:
        raise ValueError("Cost cannot be zero when calculating ROI.")

    net_profit = g - c
    roi_percent = (net_profit / c) * 100.0
    multiple = g / c

    return {
        "total_cost": round(c, 2),
        "total_gain": round(g, 2),
        "net_profit": round(net_profit, 2),
        "roi_percent": round(roi_percent, 2),
        "investment_multiple": round(multiple, 2),
        "is_profitable": net_profit > 0,
    }


def convert_units(value: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
    """
    Convert between common measurement units:
    Length: km, m, cm, mm, mile, foot, inch, yard
    Weight: kg, g, mg, lb, oz, ton
    Temperature: C, F, K
    Digital: bytes, kb, mb, gb, tb
    """
    v = float(value)
    fu = from_unit.strip().lower()
    tu = to_unit.strip().lower()

    # Temperature handling
    if fu in ("c", "celsius") and tu in ("f", "fahrenheit"):
        res = (v * 9 / 5) + 32
        return {"original": f"{v} {from_unit}", "converted": f"{round(res, 2)} {to_unit}", "value": res}
    if fu in ("f", "fahrenheit") and tu in ("c", "celsius"):
        res = (v - 32) * 5 / 9
        return {"original": f"{v} {from_unit}", "converted": f"{round(res, 2)} {to_unit}", "value": res}
    if fu in ("c", "celsius") and tu in ("k", "kelvin"):
        res = v + 273.15
        return {"original": f"{v} {from_unit}", "converted": f"{round(res, 2)} {to_unit}", "value": res}

    # Length base: meters
    length_factors = {
        "m": 1.0, "meter": 1.0, "meters": 1.0,
        "km": 1000.0, "kilometer": 1000.0,
        "cm": 0.01, "centimeter": 0.01,
        "mm": 0.001, "millimeter": 0.001,
        "mile": 1609.344, "miles": 1609.344,
        "ft": 0.3048, "foot": 0.3048, "feet": 0.3048,
        "inch": 0.0254, "inches": 0.0254, "in": 0.0254,
        "yard": 0.9144, "yards": 0.9144, "yd": 0.9144,
    }

    # Weight base: kilograms
    weight_factors = {
        "kg": 1.0, "kilogram": 1.0, "kilograms": 1.0,
        "g": 0.001, "gram": 0.001, "grams": 0.001,
        "mg": 0.000001, "milligram": 0.000001,
        "lb": 0.45359237, "pound": 0.45359237, "pounds": 0.45359237,
        "oz": 0.0283495, "ounce": 0.0283495, "ounces": 0.0283495,
        "ton": 1000.0, "tons": 1000.0,
    }

    # Digital base: bytes
    digital_factors = {
        "b": 1.0, "byte": 1.0, "bytes": 1.0,
        "kb": 1024.0, "kilobyte": 1024.0,
        "mb": 1024.0 ** 2, "megabyte": 1024.0 ** 2,
        "gb": 1024.0 ** 3, "gigabyte": 1024.0 ** 3,
        "tb": 1024.0 ** 4, "terabyte": 1024.0 ** 4,
    }

    for factor_group in (length_factors, weight_factors, digital_factors):
        if fu in factor_group and tu in factor_group:
            base_val = v * factor_group[fu]
            final_val = base_val / factor_group[tu]
            return {
                "original": f"{v} {from_unit}",
                "converted": f"{round(final_val, 4)} {to_unit}",
                "value": round(final_val, 4),
            }

    raise ValueError(f"Cannot convert between '{from_unit}' and '{to_unit}'. Incompatible or unsupported units.")


# ---------------------------------------------------------------------------
# 2. FILE TOOLS (Confined to safe workspace directory)
# ---------------------------------------------------------------------------

DEFAULT_WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "workspace"))


def _resolve_workspace_path(filename: str, workspace_dir: Optional[str] = None) -> str:
    """Safely resolves and validates that target path stays strictly inside workspace."""
    base_dir = os.path.abspath(workspace_dir or DEFAULT_WORKSPACE_DIR)
    os.makedirs(base_dir, exist_ok=True)

    # Clean filename of leading slashes or workspace prefixes
    clean_name = filename.strip()
    if clean_name.startswith("workspace/") or clean_name.startswith("workspace\\"):
        clean_name = clean_name[10:]

    target_path = os.path.abspath(os.path.join(base_dir, clean_name))

    # Path traversal protection check
    if not target_path.startswith(base_dir):
        raise PermissionError(f"Access denied: '{filename}' escapes workspace boundary.")

    return target_path


def read_file(filename: str, workspace_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Safely read the entire contents of a file within the workspace folder.
    Returns content, line count, character count, and format info.
    """
    target = _resolve_workspace_path(filename, workspace_dir)
    if not os.path.exists(target):
        raise FileNotFoundError(f"File not found in workspace: '{filename}'")

    with open(target, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    lines = content.splitlines()
    return {
        "filename": os.path.basename(target),
        "relative_path": os.path.relpath(target, os.path.dirname(DEFAULT_WORKSPACE_DIR)),
        "content": content,
        "line_count": len(lines),
        "char_count": len(content),
        "size_bytes": os.path.getsize(target),
    }


def write_file(filename: str, content: str, workspace_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Safely write text content to a file in the workspace directory.
    Creates parent directories if necessary.
    """
    target = _resolve_workspace_path(filename, workspace_dir)
    os.makedirs(os.path.dirname(target), exist_ok=True)

    with open(target, "w", encoding="utf-8") as f:
        f.write(content)

    return {
        "filename": os.path.basename(target),
        "target_path": target,
        "size_bytes": os.path.getsize(target),
        "message": f"Successfully wrote {len(content)} characters to '{os.path.basename(target)}'.",
    }


def list_files(workspace_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    List all files in the designated workspace directory with sizes and timestamps.
    """
    base_dir = os.path.abspath(workspace_dir or DEFAULT_WORKSPACE_DIR)
    os.makedirs(base_dir, exist_ok=True)

    files_info = []
    for entry in os.scandir(base_dir):
        if entry.is_file():
            stat = entry.stat()
            ext = os.path.splitext(entry.name)[1].lower()
            files_info.append({
                "name": entry.name,
                "size_bytes": stat.st_size,
                "extension": ext,
                "modified": stat.st_mtime,
            })

    return {
        "workspace_dir": base_dir,
        "total_files": len(files_info),
        "files": sorted(files_info, key=lambda x: x["name"]),
    }


def detect_file_format(filename: str, workspace_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Detect format, extension, and structure of a workspace file.
    If CSV, analyzes headers and row count.
    If JSON, analyzes top-level structure.
    """
    target = _resolve_workspace_path(filename, workspace_dir)
    if not os.path.exists(target):
        raise FileNotFoundError(f"File not found: '{filename}'")

    _, ext = os.path.splitext(target)
    ext = ext.lower().lstrip(".")

    details: Dict[str, Any] = {
        "filename": os.path.basename(target),
        "extension": ext,
        "category": "unknown",
    }

    if ext == "csv":
        details["category"] = "tabular"
        with open(target, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.reader(f)
            header = next(reader, [])
            row_count = sum(1 for _ in reader)
            details["header"] = header
            details["column_count"] = len(header)
            details["data_row_count"] = row_count
    elif ext == "json":
        details["category"] = "structured_json"
        with open(target, "r", encoding="utf-8", errors="replace") as f:
            data = json.load(f)
            details["is_list"] = isinstance(data, list)
            details["item_count"] = len(data) if isinstance(data, (list, dict)) else 1
    elif ext in ("txt", "log"):
        details["category"] = "plain_text"
    elif ext in ("md", "markdown"):
        details["category"] = "markdown_document"

    return details


# ---------------------------------------------------------------------------
# 3. RESEARCH TOOLS (Local Knowledge Base & Web Search Simulation)
# ---------------------------------------------------------------------------

KNOWLEDGE_BASE: Dict[str, Dict[str, Any]] = {
    "renewable energy": {
        "title": "Renewable Energy Technologies and Trends",
        "category": "Energy & Sustainability",
        "summary": "Renewable energy is energy derived from natural resources that replenish themselves faster than they are consumed, such as sunlight, wind, water, geothermal, and biomass.",
        "key_points": [
            "Solar and wind power are now the lowest-cost sources of new electricity generation in over 85% of the world.",
            "Solar Photovoltaic (PV) technology efficiency has grown from ~12% in 2000 to over 22-25% in modern commercial bifacial panels.",
            "Energy storage systems (Battery Energy Storage Systems - BESS), predominantly lithium-iron-phosphate (LFP), solve grid intermittency.",
            "Global installed renewable capacity crossed 3,870 Gigawatts (GW) in recent benchmarks.",
            "Levelized Cost of Electricity (LCOE) for utility-scale solar has dropped over 88% since 2010.",
            "Decentralized microgrids allow rural and industrial installations to operate independently from central grids.",
        ],
        "statistics": {
            "solar_cost_drop_since_2010": "88%",
            "global_capacity_gw": "3,870 GW",
            "top_technologies": ["Solar PV", "Onshore Wind", "Offshore Wind", "Hydroelectric", "LFP Storage"],
        },
        "sources": [
            "International Renewable Energy Agency (IRENA) - Global Energy Transition Report",
            "National Renewable Energy Laboratory (NREL) - Annual Technology Baseline",
            "BloombergNEF - Clean Energy Transition Insights",
        ],
    },
    "solar power": {
        "title": "Solar Photovoltaic and Thermal Systems",
        "category": "Energy & Sustainability",
        "summary": "Solar power converts electromagnetic radiation from the sun directly into electricity using semiconductor photovoltaic cells or concentrated solar thermal collectors.",
        "key_points": [
            "Silicon-based monocrystalline panels currently offer the highest commercial efficiency (21%-24%).",
            "Inverters convert DC electricity generated by solar arrays into standard AC power used in homes and utility grids.",
            "Maximum Power Point Tracking (MPPT) charge controllers optimize current and voltage to extract peak energy in varying sunlight.",
            "Bifacial panels capture reflected light from the ground (albedo effect), boosting output by up to 15-25%.",
        ],
        "statistics": {
            "typical_panel_lifespan_years": "25-30 years",
            "efficiency_range": "20% - 24%",
        },
        "sources": ["Solar Energy Industries Association (SEIA)", "IEEE Power and Energy Society"],
    },
    "wind energy": {
        "title": "Wind Energy Generation Systems",
        "category": "Energy & Sustainability",
        "summary": "Wind turbines harness mechanical energy from moving air currents and convert it into electrical power using generators mounted in tall nacelles.",
        "key_points": [
            "Modern utility-scale turbines generate between 2 MW and 15 MW per unit.",
            "Offshore wind farms enjoy higher and more consistent wind speeds than onshore counterparts.",
            "Capacity factors for modern offshore installations often exceed 50%.",
        ],
        "statistics": {
            "average_capacity_factor": "35% - 55%",
            "largest_offshore_turbine_capacity": "16 MW",
        },
        "sources": ["Global Wind Energy Council (GWEC)", "U.S. Department of Energy - Wind Energy Technologies"],
    },
    "python programming": {
        "title": "Python Programming Language",
        "category": "Computer Science & Software",
        "summary": "Python is a high-level, interpreted, dynamically typed programming language created by Guido van Rossum in 1991, celebrated for clean readability, rich standard library, and massive ecosystem.",
        "key_points": [
            "Readable syntax adheres to PEP 8 style standards, emphasizing code clarity over brevity.",
            "Multi-paradigm: supports object-oriented, procedural, and functional programming models.",
            "Dominates Artificial Intelligence, Machine Learning, Data Science, Automation, and Web Development (Flask, Django, FastAPI).",
            "PyPI (Python Package Index) hosts over 500,000 open-source packages accessible via pip.",
            "Modern versions (Python 3.11, 3.12, 3.13) feature significant runtime speedups, improved tracebacks, and enhanced type hints.",
            "Core data structures include lists, dictionaries, tuples, sets, and generators.",
        ],
        "statistics": {
            "created_year": "1991",
            "creator": "Guido van Rossum",
            "primary_uses": ["AI & Machine Learning", "Data Engineering", "Web Backends", "DevOps Scripting"],
        },
        "sources": [
            "Official Python Documentation (docs.python.org)",
            "Python Software Foundation (PSF)",
            "The Zen of Python (PEP 20)",
        ],
    },
    "machine learning": {
        "title": "Machine Learning Fundamentals",
        "category": "Computer Science & Software",
        "summary": "Machine Learning (ML) is a subset of artificial intelligence where algorithms improve their performance on tasks through data-driven experience rather than explicit hand-coded rules.",
        "key_points": [
            "Three main paradigms: Supervised Learning (labeled data), Unsupervised Learning (clustering/patterns), and Reinforcement Learning (reward optimization).",
            "Core workflow consists of Data Collection -> Preprocessing -> Feature Engineering -> Model Training -> Validation -> Deployment.",
            "Popular libraries: scikit-learn for traditional models, PyTorch and TensorFlow for deep learning neural networks.",
            "Evaluation metrics include Accuracy, Precision, Recall, F1-Score, ROC-AUC, and Mean Squared Error (MSE).",
        ],
        "statistics": {
            "top_frameworks": ["PyTorch", "scikit-learn", "TensorFlow", "XGBoost"],
        },
        "sources": ["Stanford CS229 Machine Learning", "Google Machine Learning Crash Course"],
    },
    "artificial intelligence agents": {
        "title": "Autonomous AI Agents and Multi-Agent Systems",
        "category": "Artificial Intelligence",
        "summary": "An AI agent is an autonomous software entity that perceives its environment, makes reasoned decisions, and executes actions using tools to accomplish designated goals.",
        "key_points": [
            "Core Agent Loop: Perception (input) -> Reasoning / Planning -> Tool Selection -> Action Execution -> Observation -> Reflection.",
            "Multi-Agent Architectures allow specialized agents (Researchers, Writers, Analysts) to collaborate via message brokers or orchestrators.",
            "Tool Calling enables agents to interact with external APIs, execute safe code, read databases, and manipulate local files.",
            "Decoupled message buses promote modularity, fault isolation, and parallel asynchronous task processing.",
            "Key design patterns include Orchestrator-Worker, Peer-to-Peer Consensus, and Hierarchical Task Networks (HTN).",
        ],
        "statistics": {
            "core_patterns": ["Orchestrator-Worker", "Message Bus", "Plan-and-Execute", "ReAct"],
        },
        "sources": ["Russell & Norvig - Artificial Intelligence: A Modern Approach", "ACM Computing Surveys on Agent Systems"],
    },
    "data science": {
        "title": "Data Science and Statistical Analytics",
        "category": "Data & Analytics",
        "summary": "Data science combines domain expertise, programming skills, and mathematics/statistics to extract meaningful actionable insights from structured and unstructured data.",
        "key_points": [
            "Exploratory Data Analysis (EDA) reveals underlying patterns, spots anomalies, and tests hypotheses using graphical representations.",
            "Data cleansing accounts for up to 60-70% of a data practitioner's daily effort.",
            "Essential Python tools: Pandas for data frames, NumPy for vectorized matrices, Matplotlib/Seaborn for data visualizations.",
        ],
        "statistics": {
            "key_tools": ["Pandas", "NumPy", "Matplotlib", "Seaborn", "Jupyter"],
        },
        "sources": ["Python for Data Analysis by Wes McKinney", "Harvard Data Science Review"],
    },
    "cybersecurity": {
        "title": "Cybersecurity Principles and Defense-in-Depth",
        "category": "Information Security",
        "summary": "Cybersecurity is the practice of protecting systems, networks, and programs from digital attacks, unauthorized access, and data corruption.",
        "key_points": [
            "The CIA Triad forms the core foundation: Confidentiality, Integrity, and Availability.",
            "Zero Trust Architecture assumes breach and verifies explicitly on every request.",
            "Defense-in-depth incorporates firewalls, encryption (TLS/AES), multi-factor authentication (MFA), and automated auditing.",
        ],
        "statistics": {
            "core_pillars": ["Confidentiality", "Integrity", "Availability"],
        },
        "sources": ["NIST Cybersecurity Framework (CSF)", "OWASP Top 10 Guidelines"],
    },
}


def knowledge_base_lookup(query: str, category: Optional[str] = None) -> Dict[str, Any]:
    """
    Search the built-in knowledge encyclopedia for relevant technical topics.
    Matches queries against titles, categories, and content keywords.
    """
    q = query.lower().strip()
    best_match_key = None
    best_score = 0

    for key, entry in KNOWLEDGE_BASE.items():
        score = 0
        if q in key or key in q:
            score += 10
        # Check title
        if any(word in entry["title"].lower() for word in q.split()):
            score += 5
        # Check summary and key points
        for point in entry["key_points"]:
            for word in q.split():
                if len(word) > 3 and word in point.lower():
                    score += 1
        if category and entry["category"].lower() == category.lower():
            score += 3

        if score > best_score:
            best_score = score
            best_match_key = key

    if not best_match_key or best_score == 0:
        # Fallback to closest match or available topics
        available = list(KNOWLEDGE_BASE.keys())
        return {
            "found": False,
            "query": query,
            "message": f"No direct match found in knowledge base. Available topics: {', '.join(available)}",
            "available_topics": available,
        }

    match_data = KNOWLEDGE_BASE[best_match_key]
    return {
        "found": True,
        "topic": best_match_key,
        "title": match_data["title"],
        "category": match_data["category"],
        "summary": match_data["summary"],
        "key_points": match_data["key_points"],
        "statistics": match_data.get("statistics", {}),
        "sources": match_data.get("sources", []),
        "relevance_score": best_score,
    }


def simulated_web_search(query: str) -> Dict[str, Any]:
    """
    Simulates a multi-engine web search returning realistic indexed search snippets.
    Provides verified factual snippets without requiring external network calls.
    """
    q = query.lower().strip()
    results = []

    # Check matches across all knowledge base entries
    for topic, entry in KNOWLEDGE_BASE.items():
        # Compute keyword overlap
        query_words = set(w for w in re.findall(r"\w+", q) if len(w) > 2)
        entry_text = (topic + " " + entry["title"] + " " + entry["summary"] + " " + " ".join(entry["key_points"])).lower()
        overlap = sum(1 for w in query_words if w in entry_text)

        if overlap > 0:
            url_slug = topic.replace(" ", "-")
            results.append({
                "title": f"{entry['title']} - Comprehensive Technical Guide",
                "url": f"https://knowledge.internal.org/{url_slug}",
                "snippet": entry["summary"] + " " + entry["key_points"][0],
                "score": overlap,
                "domain": "internal.org",
            })

    # Sort by relevance score
    results.sort(key=lambda x: x["score"], reverse=True)
    top_results = results[:4]

    if not top_results:
        top_results.append({
            "title": f"General Overview for '{query}'",
            "url": "https://knowledge.internal.org/search?q=" + query.replace(" ", "+"),
            "snippet": f"Index results matching query terms for {query}. Review knowledge repository entries.",
            "score": 1,
            "domain": "internal.org",
        })

    return {
        "query": query,
        "total_results": len(top_results),
        "results": top_results,
    }


def pattern_matching(text: str, pattern: str) -> Dict[str, Any]:
    """
    Search for regex patterns or keywords inside text and extract structured findings.
    Recognizes preset patterns: 'emails', 'numbers', 'currency', 'dates' or custom regex.
    """
    preset_patterns = {
        "emails": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        "numbers": r"[-+]?\d*\.?\d+",
        "currency": r"\$[\d,]+(?:\.\d{2})?",
        "dates": r"\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}/\d{1,2}/\d{2,4}\b",
    }

    regex_str = preset_patterns.get(pattern.lower(), pattern)
    try:
        matches = re.findall(regex_str, text)
        return {
            "pattern_type": pattern,
            "regex_used": regex_str,
            "match_count": len(matches),
            "matches": matches[:50],
        }
    except re.error as err:
        raise ValueError(f"Invalid regex pattern '{pattern}': {err}")


# ---------------------------------------------------------------------------
# 4. TEXT TOOLS (Summarization, Document Formatting, Metrics)
# ---------------------------------------------------------------------------

def summarize_text(text: str, max_sentences: int = 3) -> Dict[str, Any]:
    """
    Perform extractive text summarization based on word frequencies and sentence scoring.
    Does not require any external LLM or deep learning models.
    """
    if not text or not text.strip():
        return {"summary": "", "sentence_count": 0, "original_length": 0}

    # Split text into sentences
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    if len(sentences) <= max_sentences:
        return {
            "summary": " ".join(sentences),
            "sentence_count": len(sentences),
            "original_length": len(text),
        }

    # Stopwords filter
    stopwords = {
        "the", "is", "at", "which", "on", "and", "a", "an", "in", "to", "of", "for",
        "with", "as", "by", "that", "this", "it", "from", "are", "be", "was", "or",
    }

    # Compute word frequency
    words = [w.lower() for w in re.findall(r"\w+", text) if w.lower() not in stopwords]
    word_freq: Dict[str, int] = {}
    for w in words:
        word_freq[w] = word_freq.get(w, 0) + 1

    # Score sentences
    scored_sentences = []
    for idx, sentence in enumerate(sentences):
        sent_words = [w.lower() for w in re.findall(r"\w+", sentence)]
        score = sum(word_freq.get(w, 0) for w in sent_words)
        # Normalize slightly by length
        norm_score = score / (len(sent_words) + 1)
        scored_sentences.append((norm_score, idx, sentence))

    # Pick top N sentences preserving original chronological order
    top_scored = sorted(scored_sentences, key=lambda x: x[0], reverse=True)[:max_sentences]
    chronological = sorted(top_scored, key=lambda x: x[1])
    summary_text = " ".join([item[2] for item in chronological])

    return {
        "summary": summary_text,
        "selected_sentence_indices": [item[1] for item in chronological],
        "total_original_sentences": len(sentences),
        "summary_sentence_count": len(chronological),
    }


def format_document(
    title: str,
    sections: Dict[str, Union[str, List[str]]],
    format_type: str = "markdown",
) -> Dict[str, Any]:
    """
    Format structured data into a polished document (Markdown or Plain Text).

    Args:
        title: Document main title
        sections: Dict mapping section headings to body text or lists of bullet points
        format_type: 'markdown' or 'text'
    """
    doc_lines: List[str] = []

    if format_type.lower() == "markdown":
        doc_lines.append(f"# {title}\n")
        doc_lines.append(f"> *Generated by AI Multi-Agent System on {os.environ.get('SYSTEM_DATE', '2026')}*\n")
        doc_lines.append("## Table of Contents")
        for heading in sections.keys():
            anchor = heading.lower().replace(" ", "-").replace(":", "")
            doc_lines.append(f"- [{heading}](#{anchor})")
        doc_lines.append("\n---\n")

        for heading, content in sections.items():
            doc_lines.append(f"## {heading}\n")
            if isinstance(content, list):
                for item in content:
                    doc_lines.append(f"- {item}")
                doc_lines.append("")
            else:
                doc_lines.append(f"{str(content).strip()}\n")

        doc_lines.append("\n---\n")
        doc_lines.append("*End of Report — Multi-Agent Collaboration Pipeline*")

    else:
        # Plain text formatting
        border = "=" * 70
        doc_lines.append(border)
        doc_lines.append(title.upper().center(70))
        doc_lines.append(border)
        doc_lines.append("")

        for heading, content in sections.items():
            doc_lines.append(f"[{heading.upper()}]")
            doc_lines.append("-" * len(heading))
            if isinstance(content, list):
                for item in content:
                    doc_lines.append(f"  * {item}")
            else:
                doc_lines.append(f"  {str(content).strip()}")
            doc_lines.append("")

        doc_lines.append(border)

    final_content = "\n".join(doc_lines)
    return {
        "title": title,
        "format": format_type,
        "character_count": len(final_content),
        "line_count": len(doc_lines),
        "content": final_content,
    }


def word_count(text: str) -> Dict[str, Any]:
    """
    Analyze word count, character count, sentence count, and reading time estimate.
    """
    words = re.findall(r"\w+", text)
    sentences = [s for s in re.split(r"[.!?]+", text) if s.strip()]
    chars = len(text)
    chars_no_spaces = len(text.replace(" ", "").replace("\n", ""))

    # Average human reading speed: ~200 words per minute
    reading_time_mins = round(len(words) / 200.0, 2)

    return {
        "word_count": len(words),
        "character_count": chars,
        "character_count_no_spaces": chars_no_spaces,
        "sentence_count": len(sentences),
        "estimated_reading_time_minutes": reading_time_mins,
    }


# ---------------------------------------------------------------------------
# FACTORY REGISTRATION FUNCTIONS
# ---------------------------------------------------------------------------

def get_calculator_tools() -> List[Tool]:
    """Return all tools intended for the Calculator Agent."""
    return [
        Tool("basic_math", "Evaluate mathematical expressions safely (+, -, *, /, **, sqrt, sin, log, etc.)", basic_math, "expression: str"),
        Tool("compute_statistics", "Compute mean, median, standard deviation, variance, min, max on numbers", compute_statistics, "numbers: list[float] | str"),
        Tool("calculate_compound_interest", "Calculate compound interest with annual breakdown", calculate_compound_interest, "principal: float, annual_rate: float, time_years: float, compounding_frequency: int = 1"),
        Tool("calculate_roi", "Calculate Return on Investment (ROI) and net profit percentage", calculate_roi, "gain: float, cost: float"),
        Tool("convert_units", "Convert units of length, temperature, weight, and digital storage", convert_units, "value: float, from_unit: str, to_unit: str"),
    ]


def get_file_tools() -> List[Tool]:
    """Return all tools intended for the File Agent."""
    return [
        Tool("read_file", "Safely read the text content of a workspace file", read_file, "filename: str, workspace_dir: str = None"),
        Tool("write_file", "Safely write text content to a file in the workspace directory", write_file, "filename: str, content: str, workspace_dir: str = None"),
        Tool("list_files", "List all available files in workspace with metadata", list_files, "workspace_dir: str = None"),
        Tool("detect_file_format", "Inspect file extension, schema, and CSV/JSON structure", detect_file_format, "filename: str, workspace_dir: str = None"),
    ]


def get_research_tools() -> List[Tool]:
    """Return all tools intended for the Researcher Agent."""
    return [
        Tool("knowledge_base_lookup", "Search built-in technical encyclopedia for verified topic facts", knowledge_base_lookup, "query: str, category: str = None"),
        Tool("simulated_web_search", "Simulate web search returning snippets and sources", simulated_web_search, "query: str"),
        Tool("pattern_matching", "Extract regex patterns, emails, numbers, dates, currency from text", pattern_matching, "text: str, pattern: str"),
        Tool("summarize_text", "Extractive sentence summarizer based on frequency scoring", summarize_text, "text: str, max_sentences: int = 3"),
    ]


def get_text_tools() -> List[Tool]:
    """Return all tools intended for the Writer Agent."""
    return [
        Tool("format_document", "Generate structured Markdown or plain text documents from sections", format_document, "title: str, sections: dict, format_type: str = 'markdown'"),
        Tool("summarize_text", "Create extractive summaries from large text blocks", summarize_text, "text: str, max_sentences: int = 3"),
        Tool("word_count", "Calculate word, char, sentence counts and estimated reading time", word_count, "text: str"),
    ]


def get_all_tools() -> Dict[str, Tool]:
    """Return a dictionary of all available tools mapped by name."""
    tools_list = get_calculator_tools() + get_file_tools() + get_research_tools() + get_text_tools()
    unique_tools = {}
    for t in tools_list:
        unique_tools[t.name] = t
    return unique_tools

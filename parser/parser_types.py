from __future__ import annotations
from typing import TypedDict, List, Dict, Any, Tuple


class Calculation(TypedDict):
    code: str
    explanation: str
    result: Any
    result_show: str
    subcalculations: List[Any]
    type: str
    calculation_explanation: str
    fb_label: str
    why_line: str


class Memory(TypedDict):
    address: int
    type: str
    value: Any
    value_show: str


Variables = Dict[str, Tuple[str, int, int]]


class Statement(TypedDict):
    calculation: Calculation
    current_line: str
    memory_after: List[Memory]
    memory_before: List[Memory]
    next_line: str
    variables_after: Variables
    variables_before: Variables


EdgeReason = Tuple[int, str]
Edge = Tuple[int, int]


class LineNumber(TypedDict):
    start: int
    last: List[EdgeReason]


def empty_statement(line: int) -> Statement:
    calc: Calculation = {
        "explanation": "",
        "code": "",
        "result": "None",
        "result_show": "None",
        "type": "None",
        "subcalculations": [],
        "calculation_explanation": "",
        "fb_label": ""
    }
    empty: Statement = {
        "calculation": calc,
        "variables_before": {},
        "memory_before": [],
        "current_line": str(line),
        "variables_after": {},
        "memory_after": [],
        "next_line": ""
    }
    return empty

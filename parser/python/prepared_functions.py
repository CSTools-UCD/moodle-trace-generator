from typing import Any, List
from collections.abc import Sized

current_input: List[str]

def set_input(strs: List[str])-> None:
    global current_input
    current_input = strs

def preped_abs(num : float) -> float:
    return abs(num)

def preped_float(num: float) -> float:
    return float(num)

def preped_int(num: float) -> int:
    return int(num)

def preped_str(num : Any) -> str:
    return str(num)

def preped_len(smth: Sized) -> int:
    return len(smth)

def preped_max(*argv : float) -> float:
    return max(argv)

def preped_min(*argv: float) -> float:
    return min(argv)

def preped_sum(*argv: float) -> float:
    return sum(argv)

f = open("temp_output.txt", "w")
def preped_print(*args : Any , **kwargs : Any) -> None:
    kwargs["file"] = f
    return print(*args, **kwargs)

def preped_input(mess:str)->str:
    global current_input
    line = current_input[0]
    current_input = current_input[1:]
    return line.replace("\n","")
from typing import Any, List
from parser.parser_types import Variables, Memory
from parser.generic_parser import Parser
import parser.c.scanf as scanf
from icecream import ic
current_input: str


def set_input(strs: List[str])-> None: 
    global current_input
    current_input = "\n".join(strs)

f = open("temp/output.txt", "w")

def prepared_printf(fs: str, *argv) -> int:
    s = fs % (argv)
    return len(s), "int"

def prepared_scanf(parser: Parser,fs:str, *argv) -> int:
    global current_input
    ans = scanf.scanf(fs, current_input)
    current_input = ans[-1]
    ans = ans[:-1]
    num = len(ans)
    if len(ans) == len(argv):
        for i in range(len(ans)):
            if isinstance (ans[i], List):
                for a in range(argv[i], argv[i]+len(ans[i])):
                    parser.memory[a]["value"] = ans[i][a]
                    parser.memory[a]["value_show"] = parser.get_result_string(ans[i][a])
            else:
                parser.memory[argv[i]]["value"] = ans[i]
                parser.memory[argv[i]]["value_show"] = parser.get_result_string(ans[i])
    return num, "int"

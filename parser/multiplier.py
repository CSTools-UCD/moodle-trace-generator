import shlex
from typing import List, Tuple

def generate_from_template(code_file_name : str, param_file_name : str, question_name : str) -> List[Tuple[str,str]]:
    param_file = open(param_file_name, "r")
    lines = param_file.readlines()
    source_codes : List[Tuple[str,str]] = []
    for i, l in enumerate(lines):
        params = shlex.split(l, posix=False)
        code_file = open( code_file_name, "r" )
        code = code_file.read()
        # print(code)
        b = code.format(*params)
        gn = generated_name(i, len(lines))
        source_codes.append(( question_name + "-" + gn, b) )
    return source_codes

def generated_name(number : int, max_num : int) -> str:
    generated_name = ""
    while max_num > 1:
        generated_name = chr(ord('a') + number % 26) + generated_name
        number = number // 26
        max_num = max_num // 26
    return generated_name
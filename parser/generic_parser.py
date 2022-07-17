from typing import List, Tuple, Any, Iterable
from parser.parser_types import Statement, Variables, Calculation, Memory


class Parser(object):
    def __init__(self, types: Any, prepared_functions: Any):
        self.memory: List[Memory] = []
        self.variables: Variables = dict()
        self.types: Any = types
        self.prepared_functions = prepared_functions

    def set_input(self, strs: List[str]) -> None:
        self.prepared_functions.set_input(strs)

    def get_types(self):
        return self.types

    def parse_source(self, source_code: str) -> Tuple[List[Statement], List[str]]:
        pass

    def parse_file(self, file_name: str) -> Tuple[List[Statement], List[str]]:
        pass

    def assign_value(self, name: str, value: Any, type: str) -> None:
        in_mem = False
        address = -1
        for t in self.memory:
            if value == t["value"]:
                in_mem = True
                address = t["address"]

        if name in self.variables:
            if in_mem:
                self.variables[name] = (type, address)
            else:
                address = self.add_to_memory(value)
                self.variables[name] = (type, address)
        else:
            if in_mem:
                self.variables[name] = (type, address)
            else:
                address = self.add_to_memory(value)
                self.variables[name] = (type, address)

    def load_value(self, name: str) -> Memory:
        if name in self.variables:
            add = self.variables[name][1]
            return self.memory[add]
        else:
            return {"address": -1, "type": "?", "value": "?", "value_show": "?"}

    def load_value_from_array(self, name: str, index: int) -> Memory:
        if name in self.variables:
            add = self.variables[name][1]
            return self.memory[add+index]
        else:
            return {"address": -1, "type": "?", "value": "?", "value_show": "?"}


    def get_mem_now(self) -> List[Memory]:
        mem_list: List[Memory] = []
        for m in self.memory:
            # print(m["type"])
            if m["type"] == "list":
                val = list(m["value"])
            else:
                val = m["value"]
            d: Memory = {
                "address": m["address"],
                "type": m["type"],
                "value": val,
                "value_show": m["value_show"]
            }
            mem_list.append(d)
        return mem_list

    def get_var_now(self) -> Variables:
        return self.variables.copy()

    def add_to_memory(self, value: Any) -> int:
        add = len(self.memory)
        self.memory.append({
            "address": add,
            "type": self.get_type_string(type(value)),
            "value": value,
            "value_show": Parser.get_result_string(value)})
        return add

    @staticmethod
    def get_type_string(typ: type) -> str:
        pass

    @staticmethod
    def get_operation(dic: Calculation, l: Calculation, r: Calculation, op: Any) -> str:
        pass

    @staticmethod
    def get_unary_operation(dic: Calculation, operand: Calculation, op: Any) -> str:
        pass

    @staticmethod
    def get_comparision(dic: Calculation, l: Calculation, r: Calculation, op: Any) -> str:
        pass

    @staticmethod
    def get_boolean_operation(dic: Calculation, args: List[Calculation], op: Any) -> str:
        pass

    @staticmethod
    def get_result_string(result: Any) -> str:
        if isinstance(result, str):
            return '"' + result + '"'
        elif isinstance(result, list):
            return '[' + ", ".join([Parser.get_result_string(x) for x in result]) + ']'
        else:
            return str(result)

    @staticmethod
    def flatten(l: Iterable[Any]) -> List[Any]:
        out: List[Any] = []
        for item in l:
            if isinstance(item, (list, tuple)):
                out.extend(Parser.flatten(item))
            else:
                out.append(item)
        return out

    @staticmethod
    def get_all_code_statement(st: Statement) -> List[str]:
        code_lines: List[str] = []
        calc_queue: List[Calculation] = [st["calculation"]]

        while len(calc_queue) > 0:
            code_lines.append(calc_queue[0]["code"])
            for sc in calc_queue[0]["subcalculations"]:
                calc_queue.append(sc)
            calc_queue = calc_queue[1:]
        return code_lines

    @staticmethod
    def get_all_code(ls: List[Statement]) -> List[str]:
        code_lines = []
        for st in ls:
            code_lines.extend(Parser.get_all_code_statement(st))
        return code_lines

    @staticmethod
    def get_all_code_file(ls: List[Statement]) -> List[str]:
        code_lines = [ x["calculation"]["code"] for x in ls]
        # for st in ls:
        #     code_lines.extend(Parser.get_all_code_statement(st))
        return code_lines


    @staticmethod
    def get_all_explanations_statement(st: Statement) -> List[str]:
        explain_lines: List[str] = []
        calc_queue: List[Calculation] = [st["calculation"]]

        while len(calc_queue) > 0:
            explain_lines.append(calc_queue[0]["explanation"])
            for sc in calc_queue[0]["subcalculations"]:
                calc_queue.append(sc)
            calc_queue = calc_queue[1:]
        return explain_lines

    @staticmethod
    def get_explanations_code(ls: List[Statement]) -> List[str]:
        explain_lines: List[str] = []
        for st in ls:
            explain_lines.extend(Parser.get_all_explanations_statement(st))
        return explain_lines

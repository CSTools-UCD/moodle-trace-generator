from typing import List, Tuple, Dict, Any, Mapping
from parser.generic_parser import Parser
from parser.parser_types import Statement, Calculation, Memory
from pycparser import c_ast, parse_file
import constants as c
import json
import parser.c.types as t
import parser.c.prepared_functions as p
from icecream import ic

top_level: bool = True


class CTracer(c_ast.NodeVisitor):
    def __init__(self, parser: "CParser") -> None:
        super().__init__()
        self.parser = parser

    def create_variable_declaration(self, node: c_ast.Decl) -> Tuple[Statement, Dict[str, str]]:
        line: str = str(node.coord.line)
        calc: Calculation = {
            "explanation": c.M_DEC,
            "code": "",
            "result": None,
            "result_show": self.parser.get_result_string(None),
            "type": "",
            "subcalculations": [],
            "calculation_explanation": c.EXP_VAR_DECL,
            "fb_label": ""
        }
        dic: Statement = {
            "variables_before": self.parser.get_var_now(),
            "memory_before": self.parser.get_mem_now(),
            "current_line": line,
            "calculation": calc,
            "memory_after": [],
            "variables_after": {},
            "next_line": ""
        }
        type_decl = self.visit(node.type)
        dic["calculation"]["code"] = type_decl["type"] + " " + type_decl["name"]
        dic["calculation"]["type"] = type_decl["type"]
        return dic, type_decl

    def create_array_declaration(self, node) -> Tuple[Statement, Dict[str, str]]:
        line: str = str(node.coord.line)
        calc: Calculation = {
            "explanation": c.M_ARR_DEC,
            "code": "",
            "result": None,
            "result_show": self.parser.get_result_string(None),
            "type": "",
            "subcalculations": [],
            "calculation_explanation": c.EXP_ARR_DECL,
            "fb_label": ""
        }
        dic: Statement = {
            "variables_before": self.parser.get_var_now(),
            "memory_before": self.parser.get_mem_now(),
            "current_line": line,
            "calculation": calc,
            "memory_after": [],
            "variables_after": {},
            "next_line": ""
        }
        type_decl = self.visit(node.type)
        # print(type_decl)
        calc["subcalculations"].append(type_decl['size'])
        dic["calculation"]["code"] = type_decl["type"] + " " + type_decl["name"] + "[" + type_decl["size"]["result_show"] + "]"
        dic["calculation"]["type"] = type_decl["type"] + "[]"
        return dic, type_decl

    def create_variable_declaration_initialisation(self, node) -> Tuple[Statement, Dict[str, str]]:
        interim, type_decl = self.create_variable_declaration(node)
        line: str = str(node.coord.line)
        calc: Calculation = {
            "explanation": c.M_VAR_INIT,
            "code": "",
            "result": None,
            "result_show": self.parser.get_result_string(None),
            "type": "",
            "subcalculations": [],
            "calculation_explanation": c.EXP_VAR_INIT,
            "fb_label": ""
        }
        dic: Statement = {
            "variables_before": self.parser.get_var_now(),
            "memory_before": self.parser.get_mem_now(),
            "current_line": line,
            "calculation": calc,
            "memory_after": [],
            "variables_after": {},
            "next_line": ""
        }
        # type_decl = self.visit(node.type)
        value = self.visit(node.init)
        calc["result"] = value["result"]
        calc["result_show"] = value["result_show"]
        calc["code"] = type_decl["type"] + " " + type_decl["name"] + " = " + value["result_show"]
        calc["type"] = type_decl["type"]
        calc['subcalculations'] = [interim["calculation"], value]
        dic["variables_after"] = self.parser.get_var_now()
        dic["memory_after"] = self.parser.get_mem_now()
        return dic, type_decl

    def create_array_declaration_initialisation(self, node) -> Tuple[Statement, Dict[str, str], Calculation]:
        interim, type_decl = self.create_array_declaration(node)
        line: str = str(node.coord.line)
        calc: Calculation = {
            "explanation": c.M_ARR_INIT,
            "code": "",
            "result": None,
            "result_show": self.parser.get_result_string(None),
            "type": "",
            "subcalculations": [],
            "calculation_explanation": c.EXP_ARR_INIT,
            "fb_label": ""
        }
        dic: Statement = {
            "variables_before": self.parser.get_var_now(),
            "memory_before": self.parser.get_mem_now(),
            "current_line": line,
            "calculation": calc,
            "memory_after": [],
            "variables_after": {},
            "next_line": ""
        }
        calculation = self.visit(node.init)
        calc["result"] = calculation["result"]
        calc["result_show"] = calculation["result_show"]
        calc["code"] = type_decl["type"] + " " + type_decl["name"] + "[" + type_decl["size"]["result_show"] + "]" + " = " + calculation["code"]
        calc["type"] = type_decl["type"]
        calc['subcalculations'] = [interim["calculation"], calculation]
        return dic, type_decl, calculation

    def visit_InitList(self, node: c_ast.InitList) -> Calculation:
        line: str = str(node.coord.line)
        calc: Calculation = {
            "explanation": c.M_ARR_CONST,
            "code": "",
            "result": None,
            "result_show": self.parser.get_result_string(None),
            "type": "",
            "subcalculations": [],
            "calculation_explanation": c.EXP_ARR_CONST,
            "fb_label": ""
        }
        calcs: List[Calculation] = []
        for e in node.exprs:
            calcs.append(self.visit(e))

        calc["code"] = "{ " + ", ".join([e['result_show'] for e in calcs]) + " }"
        # print(calc["code"])
        calc['subcalculations'] = calcs
        return calc

    def generic_visit(self, node: Any) -> None:
        """ This code is here as a sanity check to let me know when I have parsed something that I have not accounted
        for yet """
        print("Generic Visitor, someone needs to implement specific visiting functions for", type(node).__name__, node)
        c_ast.NodeVisitor.generic_visit(self, node)

    def visit_FileAST(self, node: c_ast.FileAST) -> List[Statement]:
        # print(node)
        execution_steps: List[Statement] = []
        for n in node.ext:
            t = self.visit(n)
            if isinstance(t, List):
                l = Parser.flatten(t)
                execution_steps.extend(l)
            else:
                execution_steps.append(t)
        return execution_steps

    def visit_FuncDef(self, node: c_ast.FuncDef) -> List[Statement]:
        l: List[Statement] = self.visit(node.body)
        return l

    def visit_Decl(self, node: c_ast.Decl) -> Statement:
        global top_level
        top_level = False
        dic: Statement
        if node.init is None:
            if isinstance(node.type, c_ast.TypeDecl):
                dic, decl = self.create_variable_declaration(node)
                self.parser.add_variable(decl["name"], decl["type"])
            else:
                dic, decl = self.create_array_declaration(node)
                self.parser.add_array_variable(decl["name"], decl["type"], decl['size']['result'])
        else:
            if isinstance(node.type, c_ast.TypeDecl):
                dic, decl = self.create_variable_declaration_initialisation(node)
                self.parser.add_variable(decl["name"], decl["type"])
                self.parser.assign_value(decl["name"], dic["calculation"]["result"])
            else:
                dic, decl, init = self.create_array_declaration_initialisation(node)
                if init['type'] == "string":
                    self.parser.add_array_variable(decl["name"], decl["type"], decl['size']['result'])
                    for i, char in enumerate(init['result']):
                        self.parser.assign_value_array(decl["name"], ord(char), i)
                else:
                    self.parser.add_array_variable(decl["name"], decl["type"], decl['size']['result'])
                    for i, calc in enumerate(init['subcalculations']):
                        self.parser.assign_value_array(decl["name"], calc['result'], i)
        dic["variables_after"] = self.parser.get_var_now()
        dic["memory_after"] = self.parser.get_mem_now()
        return dic

    def visit_TypeDecl(self, node: c_ast.TypeDecl):
        tp: str = self.visit(node.type)
        return {"name": node.declname, "type": tp}

    def visit_ArrayDecl(self, node: c_ast.ArrayDecl):
        tp: str = self.visit(node.type)
        # print(node.dim)
        size = self.visit(node.dim)
        tp["size"] = size
        return tp

    def ignore(self):
        pass

    def visit_IdentifierType(self, node: c_ast.IdentifierType) -> str:
        self.ignore()
        return node.names[0]

    def visit_Compound(self, node: c_ast.Compound) -> List[Statement]:
        execution_steps: List[Statement] = []
        for n in node.block_items:
            global top_level
            top_level = True
            t = self.visit(n)
            if isinstance(t, List):
                l = Parser.flatten(t)
                execution_steps.extend(l)
            else:
                execution_steps.append(t)
        return execution_steps

    def visit_Assignment(self, node: c_ast.Assignment) -> Statement:
        global top_level
        top_level = False
        line: str = str(node.coord.line)
        calc: Calculation = {
            "explanation": "Assignment",
            "code": "",
            "result": "",
            "result_show": "",
            "type": "",
            "subcalculations": [],
            "calculation_explanation": c.EXP_ASSIGN,
            "fb_label": ""
        }
        dic: Statement = {
            "variables_before": self.parser.get_var_now(),
            "memory_before": self.parser.get_mem_now(),
            "current_line": str(line),
            "calculation": calc,
            "memory_after": [],
            "variables_after": {},
            "next_line": ""
        }
        name: Calculation = self.visit(node.lvalue)
        expression: Calculation = self.visit(node.rvalue)
        if expression['type'] == "string":
            raise ValueError("tried to assign a string")
        if '[' in name["code"]:
            pass
            dic["calculation"]["code"] = name["code"] + " = " + self.parser.get_result_string(expression["result"])
            dic["calculation"]["result"] = expression["result"]
            dic["calculation"]["result_show"] = self.parser.get_result_string(expression["result"])
            dic["calculation"]["type"] = expression["type"]
            dic["calculation"]["subcalculations"].append(expression)
            self.parser.assign_value_array(name["code"][:name["code"].index('[')], expression["result"], name["subcalculations"][0]["result"])
        else:
            dic["calculation"]["code"] = name["code"] + " = " + self.parser.get_result_string(expression["result"])
            dic["calculation"]["result"] = expression["result"]
            dic["calculation"]["result_show"] = self.parser.get_result_string(expression["result"])
            dic["calculation"]["type"] = expression["type"]
            dic["calculation"]["subcalculations"].append(expression)
            self.parser.assign_value(name["code"], expression["result"])

        dic["variables_after"] = self.parser.get_var_now()
        dic["memory_after"] = self.parser.get_mem_now()
        return dic

    def visit_ID(self, node: c_ast.ID) -> Calculation:
        self.ignore()
        t: Memory = self.parser.load_value(node.name)
        return {
            "explanation": c.M_VAR,
            "code": node.name,
            "result": t["value"],
            "result_show": t["value_show"],
            "type": t["type"],
            "subcalculations": [],
            "calculation_explanation": c.EXP_LOAD,
            "fb_label": ""
        }

    def visit_Constant(self, node: c_ast.Constant) -> Calculation:
        value: Any
        if node.type in ("int", "short", "long"):
            value = int(node.value)
        elif node.type in ("float", "double"):
            value = float(node.value)
        elif node.type == 'string':
            value = node.value[1:-1]

        self.ignore()
        return {
            "explanation": c.M_CONST,
            "code": self.parser.get_result_string(value),
            "result": value,
            "result_show": self.parser.get_result_string(value),
            "type": node.type,
            "subcalculations": [],
            "calculation_explanation": c.EXP_CON,
            "fb_label": ""
        }

    def visit_BinaryOp(self, node: c_ast.BinaryOp):
        dic: Calculation = {
            "explanation": "",
            "code": "",
            "result": "",
            "result_show": "",
            "type": "",
            "subcalculations": [],
            "calculation_explanation": "",
            "fb_label": ""
        }
        l: Calculation = self.visit(node.left)
        dic["subcalculations"].append(l)
        r: Calculation = self.visit(node.right)
        dic["subcalculations"].append(r)

        op: str = self.parser.get_operation(dic, l, r, node.op)
        dic["result_show"] = self.parser.get_result_string(dic["result"])
        dic["code"] = self.parser.get_result_string(l["result"]) + op + self.parser.get_result_string(r["result"])
        return dic

    def visit_UnaryOp(self, node: c_ast.UnaryOp):
        # print(node)
        dic: Calculation = {
            "explanation": "",
            "code": "",
            "result": "",
            "result_show": "",
            "type": "",
            "subcalculations": [],
            "calculation_explanation": "",
            "fb_label": ""
        }
        operand: Calculation = self.visit(node.expr)
        op: str = self.parser.get_unary_operation(dic, operand, node.op)
        # print(operand)
        # print(dic)
        # print(op)
        # l: Calculation = self.visit(node.left)
        # dic["subcalculations"].append(l)
        # r: Calculation = self.visit(node.right)
        # dic["subcalculations"].append(r)

        # op: str = get_operation(dic, l, r, node.op)
        # dic["result_show"] = get_result_string(dic["result"])
        # dic["code"] = get_result_string(l["result"]) + op + get_result_string(r["result"])
        return dic

    def visit_If(self, node: c_ast.If):
        line: str = str(node.coord.line)
        expressions: List[Statement] = []
        calc: Calculation = {
            "explanation": c.M_IF,
            "code": "",
            "result": "None",
            "result_show": "None",
            "type": "None",
            "subcalculations": [],
            "calculation_explanation": c.EXP_IF,
            "fb_label": ""
        }
        dic: Statement = {
            "calculation": calc,
            "variables_before": self.parser.get_var_now(),
            "memory_before": self.parser.get_mem_now(),
            "current_line": line,
            "next_line": "",
            "variables_after": {},
            "memory_after": []
        }
        test: Calculation = self.visit(node.cond)
        dic["calculation"]["subcalculations"].append(test)
        dic["calculation"]["code"] = "if (" + self.parser.get_result_string(test["result"]) + ")"
        dic["variables_after"] = self.parser.get_var_now()
        dic["memory_after"] = self.parser.get_mem_now()

        expressions.append(dic)
        if test["result"] == 1:
            for b in node.iftrue:
                expressions.append(self.visit(b))
        if test["result"] == 0 and node.iffalse:
            for b in node.iffalse:
                expressions.append(self.visit(b))
        return expressions

    def visit_FuncCall(self, node: c_ast.FuncCall):
        id: c_ast.ID = node.name
        function_name: str = id.name
        if top_level:
            func_calc: Calculation = {"explanation": c.M_FUN, "code": "", "result": "", "result_show": "", "type": "", "subcalculations": self.visit(node.args), "calculation_explanation": c.EXP_FUNC, "fb_label": ""}
            arg_results = [self.parser.get_result_string(a["result"]) for a in func_calc["subcalculations"]]
            if "scanf" == function_name:
                cde = function_name + "(" + ", ".join(arg_results) + ")"
                func_calc["code"] = cde
                cde = function_name + "( p_a_r, " + ", ".join(arg_results) + ")"
            else:
                cde = function_name + "(" + ", ".join(arg_results) + ")"
                func_calc["code"] = cde

            dic: Statement = {
                "variables_before": self.parser.get_var_now(),
                "memory_before": self.parser.get_mem_now(),
                "current_line": str(node.coord.line),
                "calculation": func_calc,
                "variables_after": self.parser.get_var_now(),
                "memory_after": self.parser.get_mem_now(),
                "next_line": ""
            }
            run_me = "temp, typ = p.prepared_" + cde
            loc: Mapping[str, Any] = {"p_a_r": self.parser}
            # print(run_me)
            exec(run_me, globals(), loc)
            func_calc["result"] = loc['temp']
            dic["variables_after"] = self.parser.get_var_now()
            dic["memory_after"] = self.parser.get_mem_now()

            func_calc["result_show"] = self.parser.get_result_string(func_calc["result"])
            func_calc["type"] = loc['typ']
            # print(get_var_now())
            return dic
        else:
            func_calc: Calculation = {"explanation": c.M_FUN, "code": "", "result": "", "result_show": "", "type": "",
                                      "subcalculations": self.visit(node.args), "calculation_explanation": c.EXP_FUNC,
                                      "fb_label": ""}
            arg_results = [self.parser.get_result_string(a["result"]) for a in func_calc["subcalculations"]]
            cde = function_name + "(" + ", ".join(arg_results) + ")"
            func_calc["code"] = cde
            run_me = "temp, typ = p.prepared_" + cde
            loc: Mapping[str, Any] = {}
            exec(run_me, globals(), loc)
            func_calc["result"] = loc['temp']
            func_calc["result_show"] = self.parser.get_result_string(func_calc["result"])
            func_calc["type"] = loc['typ']

            return func_calc

    def visit_ExprList(self, node: c_ast.ExprList) -> List[Calculation]:
        global top_level
        top_level = False
        argument_list: List[Calculation] = []
        for a in node.exprs:
            argument_list.append(self.visit(a))
        return argument_list
    
    def get_while_condition(self, condition: Any) -> Tuple[Statement, Calculation]:
        line: str = str(condition.coord.line)
        calc : Calculation = {
            "explanation"    : c.M_WHILE,
            "code"      : "",
            "result"     : "None",
            "result_show": "None",
            "type"       : "None",
            "subcalculations"   : [],
            "calculation_explanation" : c.EXP_WHILE,
            "fb_label" : ""
        }
        dic : Statement = {
            "calculation" : calc,
            "variables_before" : self.parser.get_var_now(),
            "memory_before" : self.parser.get_mem_now(),
            "current_line" : line,
            "variables_after" : {},
            "memory_after" : [],
            "next_line" : ""
        }
        test : Calculation = self.visit(condition)
        dic["calculation"]["subcalculations"].append(test)
        dic["calculation"]["code"] = "while ("+ self.parser.get_result_string(test["result"]) + ")"
        dic["variables_after"] = self.parser.get_var_now()
        dic["memory_after"] = self.parser.get_mem_now()
        return dic, test

    def visit_While(self, n : c_ast.While) -> List[Statement]:
        expressions : List[Statement] = []
        test_state, test_cond = self.get_while_condition(n.cond)
        expressions.append(test_state)
        while test_cond["result"] == 1:
            t = self.visit(n.stmt)
            if isinstance(t, List):
                l = Parser.flatten(t)
                expressions.extend(l)
            else:
                expressions.append(t)
            test_state, test_cond = self.get_while_condition(n.cond)
            expressions.append(test_state)
        return expressions

    def visit_ArrayRef(self, n : c_ast.ArrayRef) -> Calculation:
        array_name = n.name.name
        num: Calculation = self.visit(n.subscript)
        # print(array_name, num["result"])
        t: Memory = self.parser.load_value_from_array(array_name, num["result"])
        # print(t)
        ans =  {
            "explanation": c.M_LOAD_ARRAY,
            "code": array_name+"[" + num["result_show"] + "]",
            "result": t["value"],
            "result_show": t["value_show"],
            "type": t["type"],
            "subcalculations": [ num ],
            "calculation_explanation": c.EXP_LOAD_ARRAY,
            "fb_label": ""
        }
        # print(array_name, num, ans, n)
        return ans
        


class CParser(Parser):
    def __init__(self):
        super().__init__(t, p)

    def parse_source(self, source_code: str) -> Tuple[List[Statement], List[str]]:
        f = open("temp/t.c", "w")
        f.write(source_code)
        f.close()
        return self.parse_file("temp/t.c")

    def parse_file(self, file_name: str) -> Tuple[List[Statement], List[str]]:
        root = parse_file(file_name)
        # print(root)
        visitor = CTracer(CParser())
        execution_steps: List[Statement] = visitor.visit(root)
        self.memory.clear()
        self.variables.clear()
        execution_steps[0]["why_line"] ="This is the start of the program"
        for i, e in enumerate(execution_steps):
            if i < len(execution_steps) - 1:
                e["next_line"] = execution_steps[i + 1]["current_line"]
                if e["calculation"]["explanation"] in (c.M_WHILE, c.M_IF):
                    res = e["calculation"]["subcalculations"][0]["result"]
                    if res == 1:
                        res = True
                    elif res == 0:
                        res = False
                    execution_steps[i + 1]["why_line"] = "This line is executed because the condition of the previous statement was "+ str(res)
                else:
                    execution_steps[i + 1]["why_line"] = "This line was executed because it was next in the sequence"
        execution_steps[-1]["next_line"] = "Finished"
        # print(json.dumps([e for e in execution_steps if e["calculation"]["explanation"] in (c.M_WHILE, c.M_IF)], indent=2))
        line_numbers = ['0'] + [e["current_line"] for e in execution_steps] + ['-1']
        return execution_steps, line_numbers

    def add_variable(self, name: str, var_type: str) -> int:
        add = len(self.memory)
        self.memory.append({
            "address": add,
            "type": var_type,
            "value": "?",
            "value_show": "?"
        })
        self.variables[name] = (var_type, add, 1)

    def add_array_variable(self, name: str, var_type: str, size: int) -> int:
        add = len(self.memory)
        for i in range(size):
            self.memory.append({
                "address": add + i,
                "type": var_type,
                "value": 0,
                "value_show": self.get_result_string(0)
            })
        self.variables[name] = (var_type + "[]", add, size)

    def update_memory(self, address: int, value: Any) -> None:
        val = self.memory[address]
        val["value"] = value
        val["value_show"] = self.get_result_string(value)

    def assign_value(self, name: str, value: Any) -> None:
        # print("Assigning value", value, "to name", name)
        if name in self.variables:
            address = self.variables[name][1]
            self.update_memory(address, value)
        else:
            raise ValueError("Variable does not exist in memory")

    def assign_value_array(self, name: str, value: Any, index: int) -> None:
        # print("Assigning value", value, "to name", name, "in index", index)
        if name in self.variables:
            address = self.variables[name][1]
            self.update_memory(address + index, value)
        else:
            raise ValueError("Variable does not exist in memory")

    @staticmethod
    def get_operation(dic: Calculation, left: Calculation, right: Calculation, op: str) -> str:
        pad_op: str
        if op == "+":
            pad_op = " + "
            dic["explanation"] = c.M_ADD
            dic['calculation_explanation'] = c.EXP_ADD
            dic['type'] = t.get_largest_type(left["type"], right["type"])
            dic["result"] = left["result"] + right["result"]
        elif op == '-':
            pad_op = " - "
            dic["explanation"] = c.M_SUB
            dic["result"] = left["result"] - right["result"]
            dic['calculation_explanation'] = c.EXP_SUB
            dic['type'] = t.get_largest_type(left["type"], right["type"])
        elif op == '*':
            pad_op = " * "
            dic["explanation"] = c.M_MUL
            dic['calculation_explanation'] = c.EXP_MULT
            dic["result"] = left["result"] * right["result"]
            dic['type'] = t.get_largest_type(left["type"], right["type"])
        elif op == '%':
            pad_op = " % "
            dic["explanation"] = c.M_MOD
            dic['calculation_explanation'] = c.EXP_MOD
            dic["result"] = left["result"] % right["result"]
            dic['type'] = t.get_largest_type(left["type"], right["type"])
        elif op == '/':
            pad_op = " / "
            dic["explanation"] = c.M_DIV
            dic['calculation_explanation'] = c.EXP_DIV
            if t.is_integer(left['type']) and t.is_integer(right['type']):
                dic["result"] = left["result"] // right["result"]
            else:
                dic["result"] = left["result"] / right["result"]
            dic['type'] = t.get_largest_type(left["type"], right["type"])
        else:
            if op in ("<", ">", "!=", "==", ">=", "<="):
                return CParser.get_comparision(dic, left, right, op)
            if op in ("||", "&&"):
                return CParser.get_boolean_operation(dic, left, right, op)

            raise ValueError("unsuported operation " + op)
        return pad_op

    def get_unary_operation(self, dic: Calculation, operand: Calculation, op: str) -> str:
        opp: str
        if op == "&":
            opp = "&"
            dic["explanation"] = c.M_REF
            dic["code"] = "&" + str(operand["code"])
            dic["type"] = "Address"
            dic["result"] = self.variables[operand["code"]][1]
            dic["result_show"] = CParser.get_result_string(self.variables[operand["code"]][1])
            dic['calculation_explanation'] = c.EXP_REF
        elif op == "!":
            opp = "!"
            dic["explanation"] = c.M_NOT
            dic["code"] = "!(" + operand["result_show"] + ")"
            dic["type"] = t.INT
            dic["result"] = 1 if operand["result"] == 0 else 0
            dic["result_show"] = CParser.get_result_string(dic["result"])
            dic["subcalculations"] = [operand]
            dic['calculation_explanation'] = c.EXP_NOT
        return opp

    @staticmethod
    def get_comparision(dic: Calculation, l: Calculation, r: Calculation, op: str) -> str:
        pad_op: str
        if op == "==":
            pad_op = " == "
            dic["explanation"] = c.M_EQC
            dic['calculation_explanation'] = c.EXP_EQ
            dic['type'] = t.INT
            dic["result"] = 1 if l["result"] == r["result"] else 0
        elif op == '!=':
            pad_op = " != "
            dic["explanation"] = c.M_NEC
            dic["result"] = 1 if l["result"] != r["result"] else 0
            dic['type'] = t.INT
            dic['calculation_explanation'] = c.EXP_NEQ
        elif op == '<':
            pad_op = " < "
            dic["explanation"] = c.M_LTC
            if not (t.is_number(l["type"]) and t.is_number(r["type"])):
                raise Exception()
            dic["result"] = 1 if l["result"] < r["result"] else 0
            dic['type'] = t.INT
            dic['calculation_explanation'] = c.EXP_LT
        elif op == '<=':
            pad_op = " <= "
            dic["explanation"] = c.M_LTE
            if not (t.is_number(l["type"]) and t.is_number(r["type"])):
                raise Exception()
            dic["result"] = 1 if l["result"] <= r["result"] else 0
            dic['type'] = t.INT
            dic['calculation_explanation'] = c.EXP_LTE
        elif op == '>':
            pad_op = " > "
            dic["explanation"] = c.M_GTC
            if not (t.is_number(l["type"]) and t.is_number(r["type"])):
                raise Exception()
            dic["result"] = 1 if l["result"] > r["result"] else 0
            dic['type'] = t.INT
            dic['calculation_explanation'] = c.EXP_GT
        elif op == '>=':
            pad_op = " >= "
            dic["explanation"] = c.M_GTE
            if not (t.is_number(l["type"]) and t.is_number(r["type"])):
                raise Exception()
            dic["result"] = 1 if l["result"] >= r["result"] else 0
            dic['type'] = t.INT
            dic['calculation_explanation'] = c.EXP_GTE
        else:
            raise Exception
        return pad_op

    @staticmethod
    def get_boolean_operation(dic: Calculation, l: Calculation, r: Calculation, op: str) -> str:
        pad_op: str
        if op == "&&":
            pad_op = " && "
            dic["explanation"] = c.M_AND
            dic["result"] = 1 if l["result"] != 0 and r["result"] != 0 else 0
            dic["code"] = l["result_show"] + " && " + r["result_show"]
            dic['type'] = t.INT
            dic['calculation_explanation'] = c.EXP_AND
        elif op == "||":
            pad_op = " || "
            dic["explanation"] = c.M_OR
            dic["result"] = 1 if l["result"] != 0 or r["result"] != 0 else 0
            dic["code"] = l["result_show"] + " !! " + r["result_show"]
            dic['type'] = t.INT
            dic['calculation_explanation'] = c.EXP_OR
        return pad_op


if __name__ == "__main__":
    cp = CParser()
    import json
    code = 'int main(){\n    int numbers[3] = {5,6,2};\n    int i = 0;\n    while (i < 3){\n        numbers[i] = numbers[i] * 2;\n        i = i + 1;\n    }\n}\n'
    print(code)
    cp.set_input([])
    x = cp.parse_source(code)
    print(json.dumps(x[0][2]["calculation"], indent=2))

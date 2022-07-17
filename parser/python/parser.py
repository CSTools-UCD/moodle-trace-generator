from typing import List,Tuple, Mapping, Any
import ast
from parser.generic_parser import Parser
from parser.parser_types import Statement, Calculation, Memory
import constants as c
import parser.python.types as t
import parser.python.prepared_functions as p

class PythonTracer(ast.NodeVisitor):

    def __init__(self, parser: Parser) -> None:
        super().__init__()
        self.parser: Parser = parser

    def get_while_condition(self, n: ast.expr) -> Tuple[Statement, Calculation]:
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
            "current_line" : str(n.lineno),
            "variables_after" : {},
            "memory_after" : [],
            "next_line" : ""
        }
        test : Calculation = self.visit(n)
        dic["calculation"]["subcalculations"].append(test)
        dic["calculation"]["code"] = "while "+ self.parser.get_result_string(test["result"]) + ":"
        dic["variables_after"] = self.parser.get_var_now()
        dic["memory_after"] = self.parser.get_mem_now()
        return dic, test

    def generic_visit(self, node : Any) -> None:
        """ This code is here as a sanity check to let me know when I have parsed something that I have not accounted for yet """
        print ("Generic Visitor used, someone needs to implment specific visiting functions for", type(node).__name__, node._fields)
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Module(self, node : ast.Module) -> List[Statement] :
        execution_steps : List[Statement] = []
        for n in node.body:
            t = self.visit(n)
            if isinstance(t, List):
                l = self.parser.flatten(t)
                execution_steps.extend(l)
            else:
                execution_steps.append(t)
        return execution_steps

    def visit_Assign(self, n : ast.Assign) -> Statement:
        calc : Calculation = {
            "explanation"       : "Assignment",
            "code"            : "",
            "result"            : "",
            "result_show"       : "",
            "type"             : "",
            "subcalculations"   : [],
            "calculation_explanation" : c.EXP_ASSIGN,
            "fb_label" : ""
        }
        dic : Statement = { 
            "variables_before" : self.parser.get_var_now(), 
            "memory_before" : self.parser.get_mem_now(), 
            "current_line" : str(n.lineno), 
            "calculation" : calc,
            "memory_after" : [],
            "variables_after" : {},
            "next_line" : ""
        }
        name : Calculation = self.visit(n.targets[0])
        expression : Calculation = self.visit(n.value)
        if '[' in name["code"]:
            dic["calculation"]["code"] = name["code"] + " = " + self.parser.get_result_string(expression["result"])
            dic["calculation"]["result"] = expression["result"]
            dic["calculation"]["result_show"] = self.parser.get_result_string(expression["result"])
            dic["calculation"]["type"] = expression["type"]
            dic["calculation"]["subcalculations"].append(expression)
            self.parser.assign_value_list(name["code"][:name["code"].index('[')], expression["result"], name["subcalculations"][0]["result"])
        else:
            dic["calculation"]["code"] = name["code"] + " = " + self.parser.get_result_string(expression["result"])
            dic["calculation"]["result"] = expression["result"]
            dic["calculation"]["result_show"] = self.parser.get_result_string(expression["result"])
            dic["calculation"]["type"] = expression["type"]
            dic["calculation"]["subcalculations"].append(expression)
            self.parser.assign_value(name["code"], expression["result"], expression["type"])

        dic["variables_after"] = self.parser.get_var_now()
        dic["memory_after"] = self.parser.get_mem_now()
        return dic

    def visit_BinOp(self, n : ast.BinOp) -> Calculation:
        dic : Calculation =  {
            "explanation"    : "",
            "code"       : "",
            "result"     : "",
            "result_show": "",
            "type"       : "",
            "subcalculations"   : [],
            "calculation_explanation" : "",
            "fb_label" : ""
        }
        l : Calculation = self.visit(n.left)
        dic["subcalculations"].append(l)
        r : Calculation = self.visit(n.right)
        dic["subcalculations"].append(r)

        op : str = self.parser.get_operation(dic, l, r, n.op)
        dic["result_show"] = self.parser.get_result_string(dic["result"])
        dic["code"] = self.parser.get_result_string(l["result"]) + op + self.parser.get_result_string(r["result"])
        dic["type"] = self.parser.get_type_string(type(dic["result"]))
        return dic

    def visit_UnaryOp(self, n : ast.UnaryOp) -> Calculation :
        dic: Calculation = {
            "explanation"    : "",
            "code"       : "",
            "result"     : "",
            "result_show": "",
            "type"       : "",
            "subcalculations"   : [],
            "calculation_explanation" : "",
            "fb_label" : ""
        }
        operand : Calculation = self.visit(n.operand)
        dic["subcalculations"].append(operand)

        op : str = self.parser.get_unary_operation(dic, operand, n.op)
        dic["type"] = self.parser.get_type_string(type(dic["result"]))
        return dic

    def visit_Constant(self, n : ast.Constant) -> Calculation:
        return {
            "explanation"    : c.M_CONST,
            "code"      : self.parser.get_result_string(n.value),
            "result"     : n.value,
            "result_show": self.parser.get_result_string(n.value),
            "type"      : self.parser.get_type_string(type(n.value)),
            "subcalculations"   : [],
            "calculation_explanation" : c.EXP_CON,
            "fb_label" : ""
            }
  
    def visit_Name(self, n : ast.Name) -> Calculation:
        t : Memory = self.parser.load_value(n.id)
        return {
            "explanation"    : c.M_VAR,
            "code"       : n.id,
            "result"    :  t["value"],
            "result_show": t["value_show"],
            "type"       : t["type"],
            "subcalculations"   : [],
            "calculation_explanation" : c.EXP_LOAD,
            "fb_label" : ""
            }

    def visit_Expr(self, n : ast.Expr) -> Statement:
        dic : Statement = {
            "variables_before" : self.parser.get_var_now(),
            "memory_before" : self.parser.get_mem_now(),
            "current_line" : str(n.lineno),
            "calculation" : self.visit(n.value),
            "variables_after" : self.parser.get_var_now(),
            "memory_after" : self.parser.get_mem_now(),
            "next_line" : ""
        }
        return dic

    def visit_Call(self, n : ast.Call) -> Calculation:
        if isinstance(n.func, ast.Name):
            dic : Calculation = {
                "explanation"    : c.M_FUN,
                "code"       : "",
                "result"     : "",
                "result_show": "",
                "type"       : "",
                "subcalculations"   : [],
                "calculation_explanation" : c.EXP_FUNC,
                "fb_label" : ""
            }
            for a in n.args:
                dic["subcalculations"].append(self.visit(a))
            arg_results = [ self.parser.get_result_string(a["result"]) for a in dic["subcalculations"]]
            cde = n.func.id + "(" +", ".join(arg_results) + ")"
            dic["code"] = cde
            run_me = "temp = p.preped_"+cde
            loc :Mapping[str, Any]  = {}
            exec(run_me, globals(), loc)
            dic["result"] = loc['temp']
            dic["result_show"] = self.parser.get_result_string(dic["result"])
            dic["type"] = self.parser.get_type_string(type(dic["result"]))
            return dic
        else:
            raise Exception("This operation is not supported" + str(n))

    def visit_Compare(self, n : ast.Compare) -> Calculation:
        dic : Calculation = {
            "explanation"    : "",
            "code"       : "",
            "result"     : "",
            "result_show"       : "",
            "type" : "",
            "subcalculations"   : [],
            "calculation_explanation" : "",
            "fb_label" : ""
        }
        l : Calculation = self.visit(n.left)
        dic["subcalculations"].append(l)
        r : Calculation = self.visit(n.comparators[0])
        dic["subcalculations"].append(r)

        op : str = self.parser.get_comparison(dic, l, r, n.ops[0])
        dic["result_show"] = self.parser.get_result_string(dic["result"])
        dic["code"] = str(l["result_show"]) + op + str(r["result_show"])
        dic["type"] = self.parser.get_type_string(type(dic["result"]))
        return dic

    def visit_BoolOp(self, n : ast.BoolOp) -> Calculation:
        """ Visits the left and right sides of the binary operation, then construct the return dictionary """
        dic: Calculation = {
            "explanation"    : "",
            "code"     : "",
            "result"     : "",
            "result_show":"",
            "type"      : "",
            "subcalculations"   : [],
            "calculation_explanation" : "",
            "fb_label" : ""
        }
        for v in n.values:
            vd : Calculation = self.visit(v)
            dic["subcalculations"].append(vd)


        op : str = self.parser.get_boolean_operation(dic, dic["subcalculations"], n.op)
        dic["result_show"] = self.parser.get_result_string(dic["result"])
        dic["type"] = self.parser.get_type_string(type(dic["result"]))
        return dic

    def visit_If(self, n : ast.If) -> List[Statement]:
        expressions : List[Statement] = []
        calc : Calculation = {
            "explanation"    : c.M_IF,
            "code"       : "",
            "result"     : "None",
            "result_show": "None",
            "type"       : "None",
            "subcalculations"   : [],
            "calculation_explanation" : c.EXP_IF,
            "fb_label" : ""
        }
        dic : Statement = {
            "calculation" : calc,
            "variables_before" : self.parser.get_var_now(),
            "memory_before" : self.parser.get_mem_now(),
            "current_line": str(n.lineno),
            "next_line":"",
            "variables_after":{},
            "memory_after": []
        }
        test : Calculation = self.visit(n.test)
        dic["calculation"]["subcalculations"].append(test)
        dic["calculation"]["code"] = "if "+ self.parser.get_result_string(test["result"]) + ":"
        dic["variables_after"] = self.parser.get_var_now()
        dic["memory_after"] = self.parser.get_mem_now()
        
        expressions.append(dic)
        if test["result"] == 'True' or test["result"] == True:
            for b in n.body:
                expressions.append(self.visit(b))
        if test["result"] == 'False' or test["result"] == False:
            for b in n.orelse:
                expressions.append(self.visit(b))
        return expressions

    def visit_While(self, n : ast.While) -> List[Statement]:
        expressions : List[Statement] = []
        test_state, test_cond = self.get_while_condition(n.test)
        expressions.append(test_state)
        while test_cond["result"] == 'True' or test_cond["result"] == True:
            for b in n.body:
                x = self.visit(b)
                expressions.append(x)
            test_state, test_cond = self.get_while_condition(n.test)
            expressions.append(test_state)
        return expressions

    def visit_Subscript(self, n : ast.Subscript) -> Calculation:
        lst : Calculation = self.visit(n.value)
        i : Calculation = self.visit(n.slice)
        d : Calculation = {
            "explanation"    : c.M_LOAD_LIST,
            "code"       : lst["code"] + "[" + str(i["result"]) + "]",
            "result"     : lst["result"][i["result"]],
            "result_show": self.parser.get_result_string(lst["result"][i["result"]]),
            "type"       : self.parser.get_type_string(type(lst["result"][i["result"]])),
            # "subcalculations"   : [lst,i],
            "subcalculations"   : [i],
            "calculation_explanation" : c.EXP_LOAD_LIST,
            "fb_label" : ""
            }
        return d

    def visit_List(self, n : ast.List) -> Calculation:
        elements : List[Calculation] = [self.visit(x) for x in n.elts]
        d : Calculation = {
            "explanation"    : c.M_DEF_LIST,
            "code"       : "[" + ", ".join([x["result_show"] for x in elements]) + "]",
            "result"     : [x["result"] for x in elements],
            "result_show": "[" + ", ".join([x["result_show"] for x in elements]) + "]",
            "type"       : t.LIST,
            "subcalculations"   : elements,
            "calculation_explanation" : c.EXP_DEFINE_LIST,
                "fb_label" : ""
            }
        return d

    def visit_Index(self, node: ast.Index) -> Calculation:
        return self.visit(node.value)

class PythonParser(Parser):
    def __init__(self):
        super().__init__(t, p)

    def parse_source(self, SOURCE : str) -> Tuple[List[Statement], List[str]]:
        root = ast.parse(SOURCE)                            # Parse and build the abstract syntax tree
        visitor = PythonTracer(self)
        execution_steps : List[Statement] = visitor.visit(root)
        self.memory.clear()
        self.variables.clear()

        execution_steps[0]["why_line"] ="This is the start of the program"
        for i, e in enumerate(execution_steps):
            if i < len(execution_steps) - 1:
                e["next_line"] = execution_steps[i + 1]["current_line"]
                if e["calculation"]["explanation"] in (c.M_WHILE, c.M_IF):
                    res = e["calculation"]["subcalculations"][0]["result"]
                    if res == True:
                        res = True
                    elif res == False:
                        res = False
                    execution_steps[i + 1]["why_line"] = "This line is executed because the condition of the previous statement was "+ str(res)
                else:
                    execution_steps[i + 1]["why_line"] = "This line was executed because it was next in the sequence"
        for i, e in enumerate(execution_steps):
            if i < len(execution_steps)-1:
                e["next_line"] = execution_steps[i+1]["current_line"]
        execution_steps[-1]["next_line"] = "Finished"

        line_numbers = ['0'] + [ e["current_line"] for e in execution_steps] +  ['-1']
        return execution_steps, line_numbers

    def parse_file(self, file_name : str) -> Tuple[List[Statement], List[str]]:
        f = open(file_name, "r")
        SOURCE = "".join(f.readlines())# Read the file
        f.close()
        return self.parse_source(SOURCE)

    @staticmethod
    def get_type_string(typ: type) -> str:
        if typ == int:
            return t.INT
        elif typ == str:
            return t.STRING
        elif typ == float:
            return t.FLOAT
        elif typ == bool:
            return t.BOOLEAN
        elif typ == list:
            return t.LIST
        else:
            return t.NONE
            
    @staticmethod
    def get_operation(dic :Calculation,l : Calculation, r : Calculation, op : ast.operator) -> str:
        opp : str
        if isinstance(op, ast.Add):
            opp = " + "
            if (l["type"] == t.INT or l["type"] == t.FLOAT) and (r["type"] == t.INT or r["type"] == t.FLOAT):
                dic["explanation"] = c.M_ADD
                dic['calculation_explanation'] = c.EXP_ADD
            elif l["type"] == t.STRING and r["type"] == t.STRING:
                dic["explanation"] = c.M_CON
                dic['calculation_explanation'] = c.EXP_CAT
            else:
                raise Exception()
            dic["result"] = l["result"] + r["result"]
        elif isinstance(op, ast.Sub):
            opp = " - "
            dic["explanation"] = c.M_SUB
            dic["result"] = l["result"] - r["result"]
            dic['calculation_explanation'] = c.EXP_SUB
        elif isinstance(op, ast.Mult):
            opp = " * "
            if (l["type"] == t.INT or l["type"] == t.FLOAT) and (r["type"] == t.INT or r["type"] == t.FLOAT):
                dic["explanation"] = c.M_MUL
                dic['calculation_explanation'] = c.EXP_MULT
            elif l["type"] == t.STRING and r["type"] == t.INT:
                dic["explanation"] = c.M_REP
                dic['calculation_explanation'] = c.EXP_REP
            else:
                raise Exception()
            dic["result"] = l["result"] * r["result"]
        elif isinstance(op, ast.Div):
            opp = " / "
            dic["explanation"] = c.M_DIV
            dic["result"] = l["result"] / r["result"]
            dic['calculation_explanation'] = c.EXP_DIV
        elif isinstance(op, ast.FloorDiv):
            opp = " // "
            dic["explanation"] = c.M_IDIV
            dic["result"] = l["result"] // r["result"]
            dic['calculation_explanation'] = c.EXP_IDIV
        elif isinstance(op, ast.Mod):
            opp = " % "
            dic["explanation"] = c.M_MOD
            dic["result"] = l["result"] % r["result"]
            dic['calculation_explanation'] = c.EXP_MOD
        elif isinstance(op, ast.Pow):
            opp = " ** "
            dic["explanation"] = c.M_EXP
            dic["result"] = l["result"] ** r["result"]
            dic['calculation_explanation'] = c.EXP_POW

        return opp

    @staticmethod
    def get_unary_operation(dic :Calculation,operand : Calculation, op : ast.unaryop) -> str:
        opp : str
        if isinstance(op, ast.UAdd):
            opp = "+"
            dic["explanation"] = c.M_UADD
            dic["code"] = "+"+str(operand["result"])
            dic["result"] = operand["result"]
            dic["result_show"] = PythonParser.get_result_string(operand["result"])
            dic['calculation_explanation'] = c.EXP_UADD
        elif isinstance(op, ast.USub):
            opp = "-"
            dic["explanation"] = c.M_USUB
            dic["code"] = "-"+str(operand["result"])
            dic["result"] = - operand["result"]
            dic["result_show"] = PythonParser.get_result_string(dic["result"])
            dic['calculation_explanation'] = c.EXP_USUB
        elif isinstance(op, ast.Not):
            opp = "not"
            dic["explanation"] = c.M_NOT
            dic["result"] = not (operand["result"])
            dic["code"] = "not(" +str(operand["result"])+")"
            dic["result_show"] = PythonParser.get_result_string(dic["result"])
            dic['calculation_explanation'] = c.EXP_NOT
        elif isinstance(op, ast.Invert):
            opp = "~"
            dic["explanation"] = c.M_BNOT
            dic["result"] = ~(operand["result"])
            dic["code"] = "~(" +str(operand["result"])+")"
            dic["result_show"] = PythonParser.get_result_string(dic["result"])
            dic['calculation_explanation'] = c.EXP_BNOT
        return opp

    @staticmethod
    def get_comparison(dic :Calculation,l : Calculation, r :Calculation, op : ast.cmpop) -> str:
        opp : str
        if isinstance(op, ast.Eq):
            opp = " == "
            dic["explanation"] = c.M_EQC
            dic["result"] = l["result"] == r["result"]
            dic['calculation_explanation'] = c.EXP_EQ
        elif isinstance(op, ast.NotEq):
            opp = " != "
            dic["explanation"] = c.M_NEC
            dic["result"] = l["result"] != r["result"]
            dic['calculation_explanation'] = c.EXP_NEQ
        elif isinstance(op, ast.Lt):
            opp = " < "
            dic["explanation"] = c.M_LTC
            if not ( (l["type"] == t.INT or l["type"] == t.FLOAT) and (r["type"] == t.INT or r["type"] == t.FLOAT) ):
                raise Exception()
            dic["result"] = l["result"] < r["result"]
            dic['calculation_explanation'] = c.EXP_LT
        elif isinstance(op, ast.LtE):
            opp = " <= "
            dic["explanation"] = c.M_LTE
            dic["result"] = l["result"] <= r["result"]
            dic['calculation_explanation'] = c.EXP_LTE
        elif isinstance(op, ast.Gt):
            opp = " > "
            dic["explanation"] = c.M_GTC
            dic["result"] = l["result"] > r["result"]
            dic['calculation_explanation'] = c.EXP_GT
        elif isinstance(op, ast.GtE):
            opp = " >= "
            dic["explanation"] = c.M_GTE
            dic["result"] = l["result"] >= r["result"]
            dic['calculation_explanation'] = c.EXP_GTE
        else:
            raise Exception
        return opp

    @staticmethod
    def get_boolean_operation(dic : Calculation, args : List[Calculation], op: ast.boolop) -> str:
        opp : str
        if isinstance(op, ast.And):
            opp = " and "
            dic["explanation"] = c.M_AND
            result = True
            for v in args:
                result = v["result"] and result
            dic["result"] = result
            dic["code"] = " and ".join([str(a["result"]) for a in args])
            dic['calculation_explanation'] = c.EXP_AND
        elif isinstance(op, ast.Or):
            opp = " or "
            dic["explanation"] = c.M_OR
            result = True
            for v in args:
                result = v["result"] or result
            dic["result"] = result
            dic["code"] = " or ".join([str(a["result"]) for a in args])
            dic['calculation_explanation'] = c.EXP_OR
        return opp

    def assign_value(self, name : str, value : Any, type: str) -> None:
        if type == "list":
            size = len(value)
        else:
            size = 1
        in_mem = False
        address = -1
        for t in self.memory:
            if value == t["value"]:
                in_mem = True
                address = t["address"]

        if name in self.variables:
            if in_mem:
                self.variables[name] = (type, address, size)
            else:
                address = self.add_to_memory(value)
                self.variables[name] = (type, address, size)
        else:
            if in_mem:
                self.variables[name] = (type, address, size)
            else:
                address = self.add_to_memory(value)
                self.variables[name] = (type, address, size)

    def assign_value_list(self, name: str, value: Any, index: int) -> None:
        typ, address, size = self.variables[name]
        val = self.memory[address]
        val["value"][index] = value
        val["value_show"] = self.get_result_string(val["value"])
    
    def update_memory(self, address: int, index: int, value: Any) -> None:
        val = self.memory[address]
        val["value"] = value
        val["value_show"] = self.get_result_string(value)

if __name__ == "__main__":
    pp = PythonParser()
    import json
    x=pp.parse_source("t = 53\nif not(t > 50 and t < 100):\n    print(t)")
    print(json.dumps(x[0][1]["calculation"], indent=2))
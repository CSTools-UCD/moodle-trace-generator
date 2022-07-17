from builder.variables import VarInfoBuilder
from dominate.tags import tr, td, table, th, div, h1, p
from typing import List, Set, Tuple, Dict
from parser.parser_types import Statement, Calculation
from parser.generic_parser import Parser
import constants as c
from parser.python.parser import PythonParser


class CalculationBuilder(object):
    def __init__(self, parser: Parser, reduced_fields: bool, literal_as_question: bool, code_list: List[Statement], var_builder: VarInfoBuilder) -> None:
        super().__init__()
        self.parser = parser
        self.reduced_fields = reduced_fields
        self.literal_as_question = literal_as_question
        lines, all_code, all_exp = self.get_detractors(parser, code_list)
        self.all_code: Set[str] = all_code
        self.all_explanations = all_exp
        self.lines = lines
        self.var_info_builder = var_builder

    def get_lines(self) -> Set[str]:
        return self.lines

    @staticmethod
    def sanitise_code(code: str) -> str:
        """ Catch all function for removing troublesome characters from the code that are interpreted by the cloze question format. """
        replacements = (("}", "\}"), )
        for a,b in replacements:
          code = code.replace(a, b)
        return code

    def get_calc_line(self, calculation: Calculation, depth: int, calc_table: table) -> int:
        """ A post-order traversal of the AST tree to build the calculation question table. Each execution of the
            function results in one row being added to the table. """
        for ch in [x for x in calculation["subcalculations"] if x is not None]:
            depth = self.get_calc_line(ch, depth, calc_table)
        if isinstance(calculation["result"], float):
            res = "{{1:NM:={:06.2f}:0.1~{}}}".format(calculation["result"], c.WRONG_NUM)
        else:
            res = "{1:SAC:=" + str(calculation["result_show"]) + "~#" + c.WRONG + "}"
        wrong_code = set(self.sanitise_code(code) for code in self.all_code) - { self.sanitise_code(calculation["code"]) }
        wrong_explanations = self.all_explanations - {calculation["explanation"]}
        if self.reduced_fields:
            if calculation["explanation"] == c.M_CONST and not self.literal_as_question:
                calc_table.add(tr(
                    td(str(depth), style="border: 1px solid black"),
                    td(self.sanitise_code(calculation["code"]), style="border: 1px solid black"),
                    td(str(calculation["result_show"]), style="border: 1px solid black"),
                    td(calculation["type"], style="border: 1px solid black"),
                    style="border: 1px solid black"
                ))
            else:
                calc_table.add(tr(
                    td(str(depth), style="border: 1px solid black"),
                    td('{1:MCS:=' + self.sanitise_code(calculation["code"]) + "~" + "~".join(wrong_code) + "}", style="border: 1px solid black"),
                    td(res, style="border: 1px solid black"),
                    td('{1:MCS:=' + calculation["type"] + "~" + "~".join(self.parser.get_types().getWrongTypes(calculation["type"])) + "}", style="border: 1px solid black"),
                    style="border: 1px solid black"
                ))
        else:
            if calculation["explanation"] == c.M_CONST and not self.literal_as_question:
                calc_table.add(tr(
                    td(str(depth), style="border: 1px solid black"),
                    td(calculation["explanation"], style="border: 1px solid black"),
                    td(self.sanitise_code(calculation["code"]), style="border: 1px solid black"),
                    td(str(calculation["result_show"]), style="border: 1px solid black"),
                    td(calculation["type"], style="border: 1px solid black"),
                    style="border: 1px solid black"
                ))
            else:
                calc_table.add(tr(
                    td(str(depth), style="border: 1px solid black"),
                    td('{1:MCS:=' + calculation["explanation"] + "~" + "~".join(wrong_explanations) + "}", style="border: 1px solid black"),
                    td('{1:MCS:=' + self.sanitise_code(calculation["code"]) + "~" + "~".join(wrong_code) + "}", style="border: 1px solid black"),
                    td(res, style="border: 1px solid black"),
                    td('{1:MCS:=' + calculation["type"] + "~" + "~".join(self.parser.get_types().getWrongTypes(calculation["type"])) + "}", style="border: 1px solid black"),
                    style="border: 1px solid black"
                ))
        return depth + 1

    def get_calc_file(self, code: List[Statement], calc_table: table) -> None:
        for c_i in range(len(code)):
            code[c_i]["calculation"]["subcalculations"] = []
        #names = self.var_info_builder.get_all_variables_and_addresses(code)  # This if for C TODO add flag
        variables: Dict[str,Tuple[str,int,int]] = self.var_info_builder.get_all_variables(code)
        lines, all_code, all_exp = self.get_detractors_file(self.parser, code)
        for statement in code:
            calculation = statement["calculation"]
            if isinstance(calculation["result"], float):
                res = "{{1:NM:={:06.2f}:0.1~{}}}".format(calculation["result"], c.WRONG_NUM)
            else:
                res = "{1:SAC:=" + str(calculation["result_show"]) + "~#" + c.WRONG + "}"
            wrong_code = set(self.sanitise_code(code) for code in all_code) - { self.sanitise_code(calculation["code"]) }
            # wrong_code = self.all_code - {self.sanitise_code(calculation["code"])}
            wrong_explanations = self.all_explanations - {calculation["explanation"]}
            line = set()
            line.add(statement["current_line"])
            wrong_lines = self.lines - line
            row: tr
            if self.reduced_fields:
                row = tr(
                    td('{2:MCS:=' + statement["current_line"]+"#"+statement["why_line"] + "~" + "~".join([ wl +"#"+statement["why_line"] for wl in wrong_lines]) + "}", style="border: 1px solid black"),
                    td('{1:MCS:=' + self.sanitise_code(calculation["code"]) + "~" + "~".join(wrong_code) + "}", style="border: 1px solid black"),
                    style="border: 1px solid black"
                )
            else:
                row = tr(
                    td('{2:MCS:=' + statement["current_line"] + "~" + "~".join(wrong_lines) + "}", style="border: 1px solid black"),
                    td('{1:MCS:=' + calculation["explanation"] + "~" + "~".join(wrong_explanations) + "}", style="border: 1px solid black"),
                    td('{1:MCS:=' + self.sanitise_code(calculation["code"]) + "~" + "~".join(wrong_code) + "}", style="border: 1px solid black"),
                    td(res, style="border: 1px solid black"),
                    td('{1:MCS:=' + calculation["type"] + "~" + "~".join(self.parser.get_types().getWrongTypes(calculation["type"])) + "}", style="border: 1px solid black"),
                    style="border: 1px solid black"
                )
            for v in variables:
                name, address, size = variables[v]
                if size == 1:
                    q = self.get_var_question(statement, name,3)
                    row.add(td(q, style="border: 1px solid black"))
                else:
                    if isinstance(self.parser, PythonParser):
                        for index in range(size):
                            q = self.get_list_var_question(statement, name, index,3)
                            row.add(td(q, style="border: 1px solid black"))
                    else:
                        for index in range(size):
                            q = self.get_array_var_question(statement, name, index,3)
                            row.add(td(q, style="border: 1px solid black"))
            calc_table.add(row)
        self.add_fake_calc_file(code[-1], calc_table, variables)

    def add_fake_calc_file(self, last_statement: Statement, calc_table: table, variables) -> None:
        import random
        fake_rows = random.randint(0,3)
        for i in range(fake_rows):
            calculation = last_statement["calculation"]
            res = "{0:SAC:=program finished" + "~#" + c.WRONG + "}"
            wrong_code = set(self.sanitise_code(code) for code in self.all_code)
            wrong_explanations = self.all_explanations
            line = set()
            line.add(c.M_FIN)
            wrong_lines = self.lines - line
            row: tr
            if self.reduced_fields:
                row = tr(
                    td('{0:MCS:=' +  c.M_FIN + "~" + "~".join([ wl for wl in wrong_lines]) + "}", style="border: 1px solid black"),
                    td('{0:MCS:=' +  c.M_FIN + "~" + "~".join(wrong_code) + "}", style="border: 1px solid black"),
                    style="border: 1px solid black"
                )
            else:
                row = tr(
                    td('{0:MCS:=' + c.M_FIN + "~" + "~".join(wrong_lines) + "}", style="border: 1px solid black"),
                    td('{0:MCS:=' + c.M_FIN + "~" + "~".join(wrong_explanations) + "}", style="border: 1px solid black"),
                    td('{0:MCS:=' + c.M_FIN + "~" + "~".join(wrong_code) + "}", style="border: 1px solid black"),
                    td(res, style="border: 1px solid black"),
                    td('{0:MCS:=' + c.M_FIN + "~" + "~".join(self.parser.get_types().getWrongTypes(calculation["type"])) + "}", style="border: 1px solid black"),
                    style="border: 1px solid black"
                )
            for v in variables:
                name, address, size = variables[v]
                if size == 1:
                    q = self.get_var_question(last_statement, name, 0)
                    row.add(td(q, style="border: 1px solid black"))
                else:
                    if isinstance(self.parser, PythonParser):
                        for index in range(size):
                            q = self.get_list_var_question(last_statement, name, index,3)
                            row.add(td(q, style="border: 1px solid black"))
                    else:
                        for index in range(size):
                            q = self.get_array_var_question(last_statement, name, index,3)
                            row.add(td(q, style="border: 1px solid black"))            
            calc_table.add(row)


    @staticmethod
    def get_var_question(statement: Statement, name: str, score: int) -> str:
        var_aft = statement["variables_after"]
        mem_aft = statement["memory_after"]
        var_bef = statement["variables_before"]
        mem_bef = statement["memory_before"]
        if name in var_aft:
            var_address = var_aft[name][1]
            var = mem_aft[var_address]
            if name in var_bef:
                bef_add = var_bef[name][1]
                bef_var = mem_bef[bef_add]
                if bef_var["value"] == var["value"]:
                    score = 0
            if isinstance(var["value"], float):
                res = "{{{}:NM:={:06.2f}:0.1~{}}}".format(score,var["value"], c.WRONG_NUM)
            else:
                res = "{{{}:SAC:=".format(score) + str(var["value_show"]) + "~#" + c.WRONG + "}"
        else:
            res = "?"
        return res

    @staticmethod
    def get_array_var_question(statement: Statement, name: str, index: int, score: int) -> str:
        var_aft = statement["variables_after"]
        mem_aft = statement["memory_after"]
        var_bef = statement["variables_before"]
        mem_bef = statement["memory_before"]
        if name in var_aft:
            var_address = var_aft[name][1]
            var = mem_aft[var_address + index]
            if name in var_bef:
                bef_add = var_bef[name][1]
                bef_var = mem_bef[bef_add+index]
                if bef_var["value"] == var["value"]:
                    score = 0
            if isinstance(var["value"], float):
                res = "{{{}:NM:={:06.2f}:0.1~{}}}".format(score, var["value"], c.WRONG_NUM)
            else:
                res = "{{{}:SAC:=".format(score) + str(var["value_show"]) + "~#" + c.WRONG + "}"
        else:
            res = "?"
        return res
    @staticmethod
    def get_list_var_question(statement: Statement, name: str, index: int, score: int) -> str:
        var_aft = statement["variables_after"]
        mem_aft = statement["memory_after"]
        var_bef = statement["variables_before"]
        mem_bef = statement["memory_before"]
        if name in var_aft:
            var_address = var_aft[name][1]
            var = mem_aft[var_address]
            if name in var_bef:
                bef_add = var_bef[name][1]
                bef_var = mem_bef[bef_add]
                if bef_var["value"] == var["value"]:
                    score = 0
            if isinstance(var["value"], float):
                res = "{{{}:NM:={:06.2f}:0.1~{}}}".format(score, var["value"][index], c.WRONG_NUM)
            else:
                res = "{{{}:SAC:=".format(score) + Parser.get_result_string(var["value"][index]) + "~#" + c.WRONG + "}"
        else:
            res = "?"
        return res
    def build_calc_div_line(self, code: Calculation) -> div:
        calc_div = div(style="display: flex; flex-direction: column; min-height: 200px; width:100%; float:left; padding: 10px")
        calc_div.add(div(h1("Calculations")))
        tb = table(style="float:right", width="100%")
        calc_div.add(table(tb))
        if self.reduced_fields:
            params = [th(heading, style="border: 1px solid black") for heading in ("Order", "Code Executed", "Result", "Type of Result")]
            tb.add(tr(*params, style="border: 1px solid black"))
        else:
            params = [th(heading, style="border: 1px solid black") for heading in ("Order", "Explanation", "Code Executed", "Result", "Type of Result")]
            tb.add(tr(*params, style="border: 1px solid black"))
        self.get_calc_line(code, 1, tb)
        return calc_div

    def build_calc_div_file(self, code: List[Statement]) -> div:
        calc_div = div(style="display: flex; flex-direction: column; min-height: 200px; width:100%; float:left; padding: 10px")
        calc_div.add(div(h1("Calculations and Variables")))
        for statement in code:
            statement["calculation"]["subcalculations"] = []
        # names = self.var_info_builder.get_all_variables_and_addresses(code)# This if for C TODO add flag
        variables = self.var_info_builder.get_all_variables(code)
        tb = table(style="float:right", width="100%")
        calc_div.add(table(tb))
        if self.reduced_fields:
            params = [th(heading, style="border: 1px solid black") for heading in ("Line", "Code Executed")]
            row = tr(*params, style="border: 1px solid black")
        else:
            params = [th(heading, style="border: 1px solid black") for heading in ("Line", "Explanation", "Code Executed", "Result", "Type of Result")]
            row = tr(*params, style="border: 1px solid black")

        # for n in names:
        #     row.add(th(n, style="border: 1px solid black"))

        for v in variables:
            name, address, size = variables[v]
            # print("Adding variable details for", name, address, size)
            if size == 1:
                # q = self.get_var_question(statement, name)
                # print("adding row headder for variable", name)
                # row.add(td(q, style="border: 1px solid black"))
                row.add(th(name, style="border: 1px solid black"))
            else:
                for index in range(size):
                    # q = self.get_array_var_question(statement, name, index)
                    head = name+"["+str(index)+']'
                    # print("adding row headder for array index", index, head)
                    row.add(td(head, style="border: 1px solid black"))

        tb.add(row)
        self.get_calc_file(code, tb)
        return calc_div

    @staticmethod
    def get_detractors(code_parser: Parser, code_list: List[Statement]) -> Tuple[Set[str], Set[str], Set[str]]:
        """ These lines of code build the detractors for the explanations and code portions of the questions"""
        ls = [x["current_line"] for x in code_list]
        lines: Set[str] = set()
        for l in ls:
            lines.add(str(l))
        lines.add(c.M_FIN)
        all_code = set(code_parser.get_all_code(code_list))
        all_explanations = set(code_parser.get_explanations_code(code_list))
        return lines, all_code, all_explanations

    @staticmethod
    def get_detractors_file(code_parser: Parser, code_list: List[Statement]) -> Tuple[Set[str], Set[str], Set[str]]:
        """ These lines of code build the detractors for the explanations and code portions of the questions"""
        ls = [x["current_line"] for x in code_list]
        lines: Set[str] = set()
        for l in ls:
            lines.add(str(l))
        lines.add(c.M_FIN)
        all_code = set(code_parser.get_all_code_file(code_list))
        all_code.add(c.M_FIN)
        all_explanations = set(code_parser.get_explanations_code(code_list))
        all_explanations.add(c.M_FIN)
        return lines, all_code, all_explanations
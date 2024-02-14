from dominate.tags import tr, td, table, th, div, h1
from typing import List, Dict, Tuple, Any
from parser.parser_types import Statement
from parser.generic_parser import Parser
import constants as c


class VarInfoBuilder(object):
    def __init__(self, parser: Parser) -> None:
        super().__init__()
        self.types = parser.get_types()
        self.parser = parser

    def build_var_row(self, var_name: str, var_value: Tuple[int, Any, str, str], show_value: bool) -> tr:
        """ This function creates a single row of the table for displaying variables in the question.
            The value of a variable will be shown if showValue is True and replaced with a short answer
            question type when the value is False. """
        # print(var_value)
        row = tr(td(var_value[0], style="border: 1px solid black"), td(var_name, style="border: 1px solid black"), style="border: 1px solid black")
        if show_value:
            cell = td(var_value[2], style="border: 1px solid black")
        else:
            cell = td("{1:MCS:=" + var_value[2] + "~" + "~".join(self.types.getWrongTypes(var_value[2])) + "}",
                      style="border: 1px solid black")
        row.add(cell)
        if show_value:
            cell = td(var_value[3], style="border: 1px solid black")
        else:
            if var_value[2] == 'float':
                res = "{{1:NM:={:06.2f}:0.1~{}}}".format(float(var_value[1]), c.WRONG_NUM)
            else:
                res = "{{1:SAC:={}~#{}}}".format(str(var_value[3]), c.WRONG)
            cell = td(res, style="border: 1px solid black")
        row.add(cell)
        return row

    def build_var_table(self, var_before: Dict[str, Tuple[int, Any, str, str]], changed_vars: Dict[str, Tuple[int, Any, str, str]], before: bool) -> table:
        """ This function creates a table for displaying the values of the variables in the program,
        both before and after execution of the specific line of code. """
        var_table = table(width="100%", style='border: 1px solid black')
        var_table.add(tr(th("Address", style="border: 1px solid black"), th("Name", style="border: 1px solid black"), th("Type", style="border: 1px solid black"),
                         th("Value", style="border: 1px solid black")))
        # print(var_before, changed_vars)
        for k in sorted(var_before.keys()):
            # print(before, k, changed_vars.keys())
            if not before and k in changed_vars:
                var_table.add(self.build_var_row(k, changed_vars[k], False))
            else:
                var_table.add(self.build_var_row(k, var_before[k], True))
        if not before:
            for k in sorted(changed_vars.keys()):
                if k not in var_before:
                    var_table.add(self.build_var_row(k, changed_vars[k], False))
        return var_table

    def build_var_div_before(self, sym_tab: Dict[str, Tuple[int, Any, str, str]]) -> div:
        """ Creates a div containing a table displaying all of the values of the variables used in this program """
        var_div = div(
            style="display: flex; flex-direction: column; min-height: 100px; width:100%; float:left; padding: 10px")
        var_div.add(div(h1("Variables Before Execution")))
        var_div.add(self.build_var_table(sym_tab, {}, True))
        return var_div

    def build_var_div_after(self, sym_tab: Dict[str, Tuple[int, Any, str, str]], changes: Dict[str, Tuple[int, Any, str, str]]) -> div:
        """ Creates a div containing a table displaying all of the values of the variables used in this program,
        if a value is changed in the execution of this line of code, the value is reqplaced with a question box. """
        var_div = div(
            style="display: flex; flex-direction: column; min-height: 100px; width:100%; float:left; padding: 10px")
        var_div.add(div(h1("Variables After Execution")))
        var_div.add(self.build_var_table(sym_tab, changes, False))
        return var_div

    def get_all_variables(self, code: List[Statement]) -> Dict[str, Tuple[str, int, int]]:
        var_names = dict()
        for line in code:
            for var_name in line["variables_after"]:
                if var_name in var_names:
                    address = line["variables_after"][var_name][1]
                    size = max(line["variables_after"][var_name][2], var_names[var_name][2])
                    var_names[var_name] = (var_name, address, size)
                else:
                    address = line["variables_after"][var_name][1]
                    size = line["variables_after"][var_name][2]
                    var_names[var_name] = (var_name, address, size)
        return var_names

    def get_all_variables_and_addresses(self, code: List[Statement]) -> List[str]:
        var_names = set()
        for line in code:
            for var_name in line["variables_after"]:
                address = line["variables_after"][var_name][1]
                var_names.add("{} : {}".format(address, var_name))
        return sorted(var_names)

    def get_symbol_tables(self, code: Statement) -> Tuple[Dict[str, Tuple[int, Any, str, str]], Dict[str, Tuple[int, Any, str, str]]]:
        """This  function assumes that memory is not being shown and only returns the values of the variables"""

        memory_before: Dict[int, Tuple[int, Any, str, str]] = dict()
        memory_after: Dict[int, Tuple[int, Any, str, str]] = dict()
        var_before: Dict[str, Tuple[int, Any, str, str]] = dict()
        var_after: Dict[str, Tuple[int, Any, str, str]] = dict()
        var_changes: Dict[str, Tuple[int, Any, str, str]] = dict()
        for mem_loc in code["memory_after"]:
            memory_after[mem_loc["address"]] = (mem_loc["address"], mem_loc["value"], mem_loc["type"], mem_loc["value_show"])
        for mem_loc in code["memory_before"]:
            memory_before[mem_loc["address"]] = (mem_loc["address"], mem_loc["value"], mem_loc["type"], mem_loc["value_show"])
        for var in code["variables_before"]:
            if 'char[]' in code["variables_before"][var][0]:
                add = code["variables_before"][var][1]
                array_start_address = code["variables_before"][var][1]
                memory_contents = [m[1] for m in memory_before.values()]
                string_contents = []
                for ind in range(array_start_address, len(memory_contents)):
                    if memory_contents[ind] != 0:
                        string_contents.append(memory_contents[ind])
                    else:
                        break
                val = "".join([chr(i) for i in string_contents])
                var_before[var] = (memory_before[add][1], val, 'char[]', self.parser.get_result_string(val))
            else:
                add = code["variables_after"][var][1]
                var_before[var] = memory_after[add] # TODO find out why I used memory_before here
            add = code["variables_before"][var][1]
        for var in code["variables_after"]:
            if 'char[]' in code["variables_after"][var][0]:
                add = code["variables_after"][var][1]
                array_start_address = code["variables_after"][var][1]
                memory_contents = [m[1] for m in memory_after.values()]
                string_contents = []
                for ind in range(array_start_address, len(memory_contents)):
                    if memory_contents[ind] != 0:
                        string_contents.append(memory_contents[ind])
                    else:
                        break
                val = "".join([chr(i) for i in string_contents])
                var_after[var] = (memory_after[add][1], val, 'char[]', self.parser.get_result_string(val))
            else:
                add = code["variables_after"][var][1]
                var_after[var] = memory_after[add]

        for k in var_after:
            if k not in var_before:
                var_changes[k] = var_after[k]
            elif var_after[k] != var_before[k]:
                var_changes[k] = var_after[k]

        return var_before, var_changes

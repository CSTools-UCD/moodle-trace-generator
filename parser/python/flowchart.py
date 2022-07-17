import ast
from typing import Dict, Tuple, Any
from parser.parser_types import LineNumber, Edge
from parser.generic_flowchart import FlowchartCreator


class PythonFlowCreator(FlowchartCreator):
    def __init__(self) -> None:
        super().__init__()

    def parse_source(self, source_code: str) -> Tuple[Dict[int, str], Dict[Edge, str]]:
        self.flow_edges.clear()
        self.flow_nodes.clear()
        self.flow_nodes[0] = "Start"
        root = ast.parse(source_code)
        visitor = Tracer(self)
        visitor.visit(root)
        self.flow_nodes[-1] = "End"
        return self.flow_nodes, self.flow_edges


class Tracer(ast.NodeVisitor):

    def __init__(self, creator: PythonFlowCreator) -> None:
        super().__init__()
        self.creator = creator

    def generic_visit(self, node: Any) -> None:
        """ This code is here as a sanity check to let me know when I have parsed something that I have not accounted for yet """
        print("Generic Visitor used, someone needs to implement specific visiting functions for", type(node).__name__, node._fields)
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Module(self, node: ast.Module) -> LineNumber:
        current_line: LineNumber = {"start": len(self.creator.flow_nodes), "last": [(0, "Start")]}
        for n in node.body:
            line_dict: LineNumber = self.visit(n)
            for end, why in current_line["last"]:
                self.creator.flow_edges[(end, line_dict["start"])] = why
            current_line = line_dict
        ret: LineNumber = {"start": 0, "last": [(len(self.creator.flow_nodes), "end")]}
        for end, why in current_line["last"]:
            self.creator.flow_edges[(end, -1)] = why + ", which is \nthe end of the program"
        return ret

    def visit_Assign(self, n: ast.Assign) -> LineNumber:
        self.creator.flow_nodes[n.lineno] = "Assignment"
        return {"start": n.lineno, "last": [(n.lineno, "Move to next line")]}

    def visit_Name(self, n: ast.Name) -> str:
        return n.id

    def visit_Call(self, n: ast.Call) -> str:
        return self.visit(n.func)

    def visit_Expr(self, n: ast.Expr) -> LineNumber:
        name = self.visit(n.value)
        if name and (name == "print" or name == "input"):
            self.creator.flow_nodes[n.lineno] = "IO"
        else:
            self.creator.flow_nodes[n.lineno] = "Function Call"
        return {"start": n.lineno, "last": [(n.lineno, "Move to next line")]}

    def visit_If(self, n: ast.If) -> LineNumber:
        self.creator.flow_nodes[n.lineno] = "If"
        ret: LineNumber = {"start": n.lineno, "last": []}
        current_line: LineNumber = {"start": n.lineno, "last": [(n.lineno, "True")]}
        first = True
        for b in n.body:
            line_dict = self.visit(b)
            for end, why in current_line["last"]:
                if first:
                    self.creator.flow_edges[(end, line_dict["start"])] = why
                    first = False
                else:
                    self.creator.flow_edges[(end, line_dict["start"])] = why
            current_line = line_dict
        ret["last"].extend(([(x[0], "end of if body (line " + str(n.lineno) + ")") for x in current_line["last"]]))
        current_line = {"start": n.lineno, "last": [(n.lineno, "False")]}
        if n.orelse:
            first = True
            for b in n.orelse:
                line_dict = self.visit(b)
                for end, why in current_line["last"]:
                    if first:
                        self.creator.flow_edges[(end, line_dict["start"])] = why
                        first = False
                    else:
                        self.creator.flow_edges[(end, line_dict["start"])] = why
                current_line = line_dict

        ret["last"].extend(([(x[0], "end of else body (line " + str(n.lineno) + ")") for x in current_line["last"]]))

        return ret

    def visit_While(self, n: ast.While) -> LineNumber:
        self.creator.flow_nodes[n.lineno] = "While"
        ret: LineNumber = {"start": n.lineno, "last": []}
        current_line: LineNumber = {"start": n.lineno, "last": [(n.lineno, "True")]}
        first = True
        for b in n.body:
            line_dict = self.visit(b)
            for end, why in current_line["last"]:
                if first:
                    self.creator.flow_edges[(end, line_dict["start"])] = why
                    first = False
                else:
                    self.creator.flow_edges[(end, line_dict["start"])] = why
            current_line = line_dict
        ret["last"].extend(current_line["last"])
        current_line = {"start": n.lineno, "last": [(n.lineno, "End of loop body")]}

        for end, why in current_line["last"]:
            self.creator.flow_edges[(line_dict["start"], end)] = why
        return {"start": n.lineno, "last": [(n.lineno, "False")]}

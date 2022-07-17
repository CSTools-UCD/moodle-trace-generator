from parser.generic_flowchart import FlowchartCreator
from parser.parser_types import Edge, LineNumber
from pycparser import c_ast, parse_file
from typing import Dict, Tuple, Any, List, Set

class CFlowCreator(FlowchartCreator):
  def __init__(self) -> None:
      super().__init__()
      self.lines : Set[int] = set()
      self.exit_stack : List[LineNumber] = []
      self.compound_depth : int = 0

  def parse_source(self, source_code : str) -> Tuple[Dict[int, str], Dict[Edge, str]]:
    f = open("temp/t.c","w")
    f.write(source_code)
    f.close()
    return self.parse_file("temp/t.c")

  def parse_file(self, file_name : str) -> Tuple[Dict[int, str], Dict[Edge, str]]:
    root = parse_file(file_name)
    # print(root)
    self.flow_edges.clear()
    self.flow_nodes.clear()
    self.exit_stack : List[LineNumber] = [ { "start" : 0, "last" : [ (0, " Beginning of program") ] } ]
    self.flow_nodes[0] = "Start"
    visitor = Tracer(self)
    visitor.visit(root)
    self.flow_nodes[-1] = "End"
    return self.flow_nodes, self.flow_edges


class Tracer(c_ast.NodeVisitor):

  def __init__(self, creator: CFlowCreator) -> None:
      super().__init__()
      self.creator = creator

  def visit_FileAST(self, node: c_ast.FileAST):
    for ext in node.ext:
        if type(ext) == c_ast.FuncDef:
            self.visit_FuncDef(ext)
        elif type(ext) == c_ast.Decl:
            self.visit_Decl(ext)
        else:
            raise Exception("unhandled ast node type  %s" % str(ext))

  def visit_FuncDef(self, node : c_ast.FuncDef):
    self.visit(node.body)

  def visit_Decl(self, node : c_ast.Decl):
    line = node.coord.line
    self.creator.lines.add(line)
    if node.init:
      self.creator.flow_nodes[line] = "Variable Declaration and Assignment"
    else:
      self.creator.flow_nodes[line] = "Variable Declaration"
    return {"start" :line, "last" : [(line, " Move to next line")]}

  def visit_Assignment(self, node : c_ast.Assignment) -> LineNumber:
    line = node.coord.line
    self.creator.lines.add(line)
    self.creator.flow_nodes[line] = "Assignment"
    return {"start" :line, "last" : [(line, " Move to next line")]}

  def visit_Compound(self, node : c_ast.Compound):
    current_line = self.creator.exit_stack.pop()
    for s in node.block_items:
      line_dict : LineNumber  = self.visit(s)
      for end, why in current_line["last"]:
        if (end, line_dict["start"]) in self.creator.flow_edges:
          self.creator.flow_edges[(end, line_dict["start"])] = self.creator.flow_edges[(end, line_dict["start"])] + "\nand " + why
        else:
          self.creator.flow_edges[(end, line_dict["start"])] = why
      current_line = line_dict
    if self.creator.compound_depth == 0:
      last_line = max(self.creator.lines)
      for end, why in current_line["last"]:
        if (end, line_dict["start"]) in self.creator.flow_edges:
          self.creator.flow_edges[(end, -1)] = self.creator.flow_edges[(end, line_dict["start"])] + "\nand " + why + +", which is \nthe end of the program"
        else:
          self.creator.flow_edges[(end, -1)] = why+", which is <br/>the end of the program"
    return current_line

  def visit_If(self, n : c_ast.If) -> LineNumber:
    line = n.coord.line
    self.creator.lines.add(line)
    self.creator.flow_nodes[line] = "If"
    ret: LineNumber = {"start" :line, "last" : []}
    self.creator.exit_stack.append({ "start" : line, "last" : [ (line, "True" ) ] })
    global compound_depth
    self.creator.compound_depth += 1
    curr : LineNumber = self.visit(n.iftrue)
    ret["last"].extend( ([ (x[0],x[1] +"<br/> and end of if ({}) body".format(line)) if "End" in x[1] else (x[0], " End of if ({}) body".format(line)) for x in curr["last"]] ) )
    if n.iffalse:
      self.creator.exit_stack.append({ "start" : line, "last" : [ (line, "False" ) ] })
      curr : LineNumber = self.visit(n.iffalse)
      ret["last"].extend( ([ (x[0],x[1] +"<br/> and end of else ({}) body".format(line)) if "End" in x[1] else (x[0], " End of else ({}) body".format(line)) for x in curr["last"]] ) )
    else:
      ret["last"].extend( [ (line, "False" ) ])
    self.creator.compound_depth -= 1
    return ret

  def visit_While(self, n : c_ast.While) -> LineNumber:
    line = n.coord.line
    self.creator.lines.add(line)
    self.creator.flow_nodes[line] = "While"
    ret: LineNumber = {"start" :line, "last" : []}
    self.creator.exit_stack.append({ "start" : line, "last" : [ (line, "True" ) ] })
    global compound_depth
    self.creator.compound_depth += 1
    curr : LineNumber = self.visit(n.stmt)
    ret["last"].extend( ([ (x[0],x[1] +"<br/> and end of while ({}) body".format(line)) if "End" in x[1] else (x[0], " End of while ({}) body".format(line)) for x in curr["last"]] ) )
    # self.creator.ic(ret)
    for end, why in ret["last"]:
      self.creator.flow_edges[( end,ret["start"])] = why

    ret["last"] = [ (line, "False" ) ]
    self.creator.compound_depth -= 1
    return ret

  def visit_FuncCall(self, node: c_ast.FuncCall):
    line = node.coord.line
    self.creator.lines.add(line)
    self.creator.flow_nodes[line] = "Function Called"
    return {"start" :line, "last" : [(line, " Move to next line")]}

  def generic_visit(self, node : Any) -> None:
    """ This code is here as a sanity check to let me know when I have parsed something that I have not accounted for yet """
    print ("Generic Visitor used, someone needs to implment specific visiting functions for", type(node).__name__)

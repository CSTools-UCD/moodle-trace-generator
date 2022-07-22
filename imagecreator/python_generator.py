import shlex
import base64
import random
from imagecreator.image_generator import ImageGenerator
from typing import List, Dict, Tuple, Any
from copy import deepcopy
from graphviz import Source
from dominate.tags import img, style, div, button, span, script, br
from xml.dom.minidom import Element, parseString, Comment
from xml.dom import getDOMImplementation
from builder.extra_tags import scrpt, CDATA
from pygments.lexers import PythonLexer
from parser.parser_types import Edge, Calculation, Statement, empty_statement
from dominate.util import raw
from dominate.svg import svg, text, g, tspan, defs, rect
from pygments.token import Text, Operator, Keyword, Name, String, Number, Punctuation
from parser.generic_flowchart import FlowchartCreator


class PythonImageGenerator(ImageGenerator):
    def __init__(self, flow_generator: FlowchartCreator) -> None:
        super().__init__(flow_generator)

    def _get_tspan_token(self, token_type: Any , token: str) -> tspan:
        if token_type in (Text, Name, Operator, Punctuation):
            if token.count(' ') == len(token):
                return tspan(raw("&#160;" * len(token)), font_size='18px', fill=self.NORMAL_COLOUR)
            elif token == '\t':
                return tspan(raw("&#160;" * 4), font_size='18px', fill=self.NORMAL_COLOUR)
            else:
                return tspan(token, font_size='18px', fill=self.NORMAL_COLOUR)
        elif token_type in (String.Double, Number.Float):
            return tspan(token, font_size='18px', fill=self.STRING_COLOUR)
        elif token_type == Number.Integer:
            return tspan(token, font_size='18px', fill=self.NUMBER_COLOUR)
        elif token_type in (Name.Builtin, Name.Builtin.Pseudo):
            return tspan(token, font_size='18px', fill=self.FUNCTION_COLOUR)
        elif token_type in (Keyword, Operator.Word, Keyword.Constant):
            return tspan(token, font_size='18px', fill=self.KEYWORD_COLOUR)

            Token.Name.Builtin.Pseudo
        else:
            raise Exception("token not supported {} {}".format(token, token_type))

    def _add_code_text(self, text_group: g, source: str) -> int:
        pl = PythonLexer()
        code_tokens: List[Tuple[int, Any, str]] = list(pl.get_tokens_unprocessed(source))
        h = self.STARTING_HEIGHT
        line_number = 1
        new_line = True
        line = None
        while len(code_tokens) > 0:
            position, token_type, token = code_tokens[0]
            code_tokens = code_tokens[1:]
            if new_line:
                line = text(str(line_number), tspan(raw("&#160;" * 2)), font_size='12px', fill=self.LINE_COLOUR, x=self.LINE_NUMBER_START_DISTANCE, y=h + self.ADJUSTMENT)
                text_group.add(line)
                line_number = line_number + 1
                new_line = False

            if token_type == Text and token == '\n':
                new_line = True
                h = h + self.LINE_SEPARATION
                continue
            
            token_tspan = self._get_tspan_token(token_type, token)
            line.add(token_tspan)
        return h

    def get_all_animation_list(self, code: List[Statement], source_code: str) -> div:
        nodes, edges = self.flow.parse_source(source_code)
        flowchart_svg_string = self.dot_to_svg_string(self._generate_flowchart_dot_string(nodes, edges))
        flowchart_svg_xml = self.remove_xml_comments(parseString(flowchart_svg_string))
        frame_css_dict : Dict[int, str] = self._generate_animation_css_list(code, self.NODE_NORMAL_COLOUR, self.HIGHLIGHT_COLOUR)
        flowchart_svg_tag = flowchart_svg_xml.getElementsByTagName("svg")[0]
        graph_g = flowchart_svg_xml.getElementsByTagName("g")[0]
        w, gr = self.generate_code_table_animation_svg_string(source_code, code)
        code_table_svg_tag = self.remove_xml_comments(parseString(gr))
        code_table_g_tag = code_table_svg_tag.getElementsByTagName("g")[0]
        impl = getDOMImplementation()
        new_svg_document = impl.createDocument(None, "svg", None)
        for key, val in flowchart_svg_tag.attributes.items():
            if key == "width":
                flow_width = int(val[:-2])
                code_table_g_tag.setAttribute("transform", "translate({} 0) scale(2 2) rotate(0) ".format(flow_width))
                new_width = str(flow_width + w * 2) + "pt"
                new_svg_document.firstChild.setAttribute(key, new_width)
            elif key.lower() == "viewbox":
                new_view = " ".join([str(float(a) + w * 2) if i == 2 else a for i, a in enumerate(val.split(" "))])
                new_svg_document.firstChild.setAttribute(key, new_view)
            else:
                new_svg_document.firstChild.setAttribute(key, val)

        code_table_group_string = ''.join([line for line in code_table_g_tag.toprettyxml(indent='').split('\n') if line.strip()])
        ast_group_string = ''.join([line for line in graph_g.toprettyxml(indent='').split('\n') if line.strip()])
        svg_string = ''.join([line for line in new_svg_document.toprettyxml(indent='').split('\n') if line.strip()])
        svg_frames: Dict[int, str] = {}
        for key, val in frame_css_dict.items():
            defs_string = defs(style(CDATA(self.STYLESHEET.format(val)), type="text/css")).render(xhtml=True)
            svg_frames[key] = str(base64.b64encode(self.pretty_xml(self.remove_xml_comments(parseString(svg_string[:-2] + ">" + code_table_group_string + ast_group_string + defs_string + "</svg>"))).encode('utf8')))[2:-1]
        return svg_frames
    

    def get_all_animation(self, code: List[Statement], source_code: str) -> str:
        nodes, edges = self.flow.parse_source(source_code)
        flowchart_svg_string = self.dot_to_svg_string(self._generate_flowchart_dot_string(nodes, edges))
        flowchart_svg_xml = self.remove_xml_comments(parseString(flowchart_svg_string))
        css_anim_string = self._generate_animation_css(code, self.NODE_NORMAL_COLOUR, self.HIGHLIGHT_COLOUR)
        flowchart_svg_tag = flowchart_svg_xml.getElementsByTagName("svg")[0]
        graph_g = flowchart_svg_xml.getElementsByTagName("g")[0]
        w, gr = self.generate_code_table_animation_svg_string(source_code, code)
        code_table_svg_tag = self.remove_xml_comments(parseString(gr))
        code_table_g_tag = code_table_svg_tag.getElementsByTagName("g")[0]
        impl = getDOMImplementation()
        new_svg_document = impl.createDocument(None, "svg", None)
        for key, val in flowchart_svg_tag.attributes.items():
            if key == "width":
                flow_width = int(val[:-2])
                code_table_g_tag.setAttribute("transform", "translate({} 0) scale(2 2) rotate(0) ".format(flow_width))
                new_width = str(flow_width + w * 2) + "pt"
                new_svg_document.firstChild.setAttribute(key, new_width)
            elif key.lower() == "viewbox":
                new_view = " ".join([str(float(a) + w * 2) if i == 2 else a for i, a in enumerate(val.split(" "))])
                new_svg_document.firstChild.setAttribute(key, new_view)
            else:
                new_svg_document.firstChild.setAttribute(key, val)

        code_table_group_string = ''.join(
            [line for line in code_table_g_tag.toprettyxml(indent='').split('\n') if line.strip()])
        ast_group_string = ''.join([line for line in graph_g.toprettyxml(indent='').split('\n') if line.strip()])
        defs_string = defs(style(CDATA(self.STYLESHEET.format(css_anim_string)), type="text/css")).render(xhtml=True)
        svg_string = ''.join([line for line in new_svg_document.toprettyxml(indent='').split('\n') if line.strip()])
        pretty = self.pretty_xml(self.remove_xml_comments(parseString(svg_string[:-2] + ">" + code_table_group_string + ast_group_string + defs_string + "</svg>")))
        return pretty
        # byte_array = base64.b64encode(pretty.encode('utf8'))
        # return str(byte_array)[2:-1]


    def generate_code_table_animation_svg_string(self, source: str, code_list: List[Statement]) -> Tuple[float, str]:
        variables = code_list[-1]["variables_after"].keys()
        code_list_copy: List[Statement] = [empty_statement(0)] + deepcopy(code_list) + [empty_statement(int(code_list[-1]["current_line"]) + 1)]
        lines = source.splitlines()
        frames = len(lines) + 2
        exe_code_len = [len(stat["calculation"]["code"]) * (self.CHAR_WIDTH + 2) + 90 for stat in code_list_copy]
        height = frames * self.LINE_SEPARATION + self.LINE_SEPARATION * (len(variables) + 1)
        width = max([len(line) * self.CHAR_WIDTH + self.CODE_START_DISTANCE * 2 for line in lines] + exe_code_len + [256])

        code_svg: svg = svg(id="svg", width=width, height=height, viewBox="0.00 0.00 {} {}".format(width, height), xmlns="http://www.w3.org/2000/svg")
        alt_svg = g(id="code_table")
        code_svg += alt_svg
        # animation_string = self._generate_animation_css(code_list, self.BACKGROUND_COLOUR, self.CODE_HIGHLIGHT_COLOUR)
        # code_svg = defs(style(CDATA(self.STYLESHEET.format(animation_string)), type="text/css"))
        alt_svg += rect(fill=self.BACKGROUND_COLOUR, height=height, width=width, x=0, y=0)
        for i in range(frames):
            alt_svg += rect(fill=self.CODE_HIGHLIGHT_COLOUR, height=self.LINE_SEPARATION + 1, width=width, x=0, y=i * self.LINE_SEPARATION,
                            visibility="hidden", opacity=0.5, _class="codeline{}".format(i))
        text_group = g(_class="normal")
        alt_svg += text_group
        h = self._add_code_text(text_group, source)
        table = g()
        h = h + self.LINE_SEPARATION
        table += rect(fill=self.NODE_NORMAL_COLOUR, height=self.LINE_SEPARATION * (len(variables) + 1), width=width, x=0, y=h, stroke=self.BACKGROUND_COLOUR)

        table += rect(fill=self.BACKGROUND_COLOUR, height=self.LINE_SEPARATION, width=len(" Code: ") * self.CHAR_WIDTH, x=0, y=h, stroke=self.NODE_NORMAL_COLOUR)
        table += text("Code:", font_size='18px', fill=self.NODE_NORMAL_COLOUR, x=self.CHAR_WIDTH, y=h + self.ADJUSTMENT, _class="alternate")
        table += rect(fill=self.BACKGROUND_COLOUR, height=self.LINE_SEPARATION, width=width - (len(" Code: ") * self.CHAR_WIDTH),
                      x=len(" Code: ") * self.CHAR_WIDTH, y=h, stroke=self.NODE_NORMAL_COLOUR)
        for i, stat in enumerate(code_list_copy):
            text_tag = text(font_size='18px', fill=self.BACKGROUND_COLOUR, x=len(" Code:   ") * self.CHAR_WIDTH, y=h + self.ADJUSTMENT, _class="alternate code_display{}".format(i), visibility="hidden")
            pl = PythonLexer()
            code_tokens: List[Tuple[int, Any, str]] = list(pl.get_tokens_unprocessed(stat["calculation"]["code"]))
            while len(code_tokens) > 0:
                position, token_type, token = code_tokens[0]
                code_tokens = code_tokens[1:]
                token_tspan = self._get_tspan_token(token_type, token)
                text_tag +=token_tspan
            table += text_tag
            # table += text(stat["calculation"]["code"], font_size='18px', fill=self.BACKGROUND_COLOUR, x=len(" Code:   ") * self.CHAR_WIDTH,
            #               y=h + self.ADJUSTMENT, _class="alternate code_display{}".format(i), visibility="hidden")

        for i, v in enumerate(variables):
            h = h + self.LINE_SEPARATION
            table += rect(fill=self.BACKGROUND_COLOUR, height=self.LINE_SEPARATION, width=len(" Code: ") * self.CHAR_WIDTH, x=0, y=h, stroke=self.NODE_NORMAL_COLOUR)
            table += text(v, font_size='18px', fill=self.NODE_NORMAL_COLOUR, x=self.CHAR_WIDTH, y=h + self.ADJUSTMENT, _class="alternate")
            table += rect(fill=self.BACKGROUND_COLOUR, height=self.LINE_SEPARATION, width=width - (len(" Code: ") * self.CHAR_WIDTH),
                          x=len(" Code: ") * self.CHAR_WIDTH, y=h, stroke=self.NODE_NORMAL_COLOUR)
            for vn, stat in enumerate(code_list_copy):
                if v in stat["variables_after"]:
                    text_tag = text(font_size='18px', fill=self.BACKGROUND_COLOUR, x=len(" Code:   ") * self.CHAR_WIDTH, y=h + self.ADJUSTMENT, _class="alternate var_display{}_{}".format(vn, i), visibility="hidden")
                    pl = PythonLexer()
                    code_tokens: List[Tuple[int, Any, str]] = list(pl.get_tokens_unprocessed(stat["memory_after"][stat["variables_after"][v][1]]["value_show"]))
                    while len(code_tokens) > 0:
                        position, token_type, token = code_tokens[0]
                        code_tokens = code_tokens[1:]
                        token_tspan = self._get_tspan_token(token_type, token)
                        text_tag +=token_tspan
                    table += text_tag
                    # table += text(stat["memory_after"][stat["variables_after"][v][1]]["value_show"], font_size='18px',
                    #               fill=self.BACKGROUND_COLOUR, x=len(" Code:   ") * self.CHAR_WIDTH, y=h + self.ADJUSTMENT,
                    #               _class="alternate var_display{}_{}".format(vn, i), visibility="hidden")
                else:
                    table += text("?", font_size='18px', fill=self.NODE_NORMAL_COLOUR, x=len(" Code:   ") * self.CHAR_WIDTH, y=h + self.ADJUSTMENT,
                                  _class="alternate var_display{}_{}".format(vn, i), visibility="hidden")
        alt_svg += table
        return width, code_svg.render(xhtml=True)

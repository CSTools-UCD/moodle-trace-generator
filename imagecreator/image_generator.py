import base64
import random
from dominate.tags import img, style,  button, span, br, div
from builder.extra_tags import CDATA, scrpt
from dominate.svg import svg, text, g, tspan, defs, rect
from copy import deepcopy
from typing import Dict, List
from parser.parser_types import Edge, Statement, Tuple, Calculation, empty_statement
from graphviz import Source
from xml.dom.minidom import Element, parseString, Comment
from parser.generic_flowchart import FlowchartCreator

NO_COPY = "svg text {{ -webkit-user-select: none; -moz-user-select: none; -ms-user-select: none; user-select: none; }} svg text::selection {{ background: none; }}"
NORMAL_STYLE = ' .normal {{ font-family: "Courier"; font-size: 18; }}'
JS_TEMPLATE = """
  let map_{0:03d} = {1};
  let timer_{0:03d};
  let index_{0:03d} = 0;
  let speed_{0:03d} = 1000;
  document.getElementById("image_{0:03d}").src = 'data:image/svg+xml;base64,' + map_{0:03d}[index_{0:03d}] + '';
  document.getElementById("frame_num_{0:03d}").textContent = 0
  document.getElementById("frame_max_{0:03d}").textContent = map_{0:03d}.length - 1
  function forward_{0:03d}() {{
    index_{0:03d} = (index_{0:03d} + 1) % map_{0:03d}.length;
    document.getElementById("image_{0:03d}").src = 'data:image/svg+xml;base64,' + map_{0:03d}[index_{0:03d}] + '';
    document.getElementById("frame_num_{0:03d}").textContent = index_{0:03d}
  }}
  function back_{0:03d}() {{
    index_{0:03d} = index_{0:03d} - 1 < 0 ? map_{0:03d}.length - 1 : index_{0:03d} - 1;
    document.getElementById("image_{0:03d}").src = 'data:image/svg+xml;base64,' + map_{0:03d}[index_{0:03d}] + '';
    document.getElementById("frame_num_{0:03d}").textContent = index_{0:03d}
  }}
  function start_{0:03d}() {{
    index_{0:03d} = 0;
    document.getElementById("image_{0:03d}").src = 'data:image/svg+xml;base64,' + map_{0:03d}[index_{0:03d}] + '';
    document.getElementById("frame_num_{0:03d}").textContent = index_{0:03d}
  }}
  function end_{0:03d}() {{
    index_{0:03d} = map_{0:03d}.length - 1;
    document.getElementById("image_{0:03d}").src = 'data:image/svg+xml;base64,' + map_{0:03d}[index_{0:03d}] + '';
    document.getElementById("frame_num_{0:03d}").textContent = index_{0:03d}
  }}
  function play_{0:03d}() {{
    document.getElementById("playButton_{0:03d}").disable = true
    document.getElementById("stopButton_{0:03d}").disable = false
    forward_{0:03d}();
    clearInterval(timer_{0:03d});
    timer_{0:03d} = setTimeout(play_{0:03d}, speed_{0:03d});
  }}
  function stop_{0:03d}() {{
    document.getElementById("playButton_{0:03d}").disable = false
    document.getElementById("stopButton_{0:03d}").disable = true
    clearInterval(timer_{0:03d});
  }}
"""

class ImageGenerator(object):
    def __init__(self, flow_generator: FlowchartCreator) -> None:
        super().__init__()
        print("here", flow_generator)
        self.flow = flow_generator
        self.CHAR_WIDTH = 10
        self.LINE_SEPARATION = 22
        self.STARTING_HEIGHT = self.LINE_SEPARATION
        self.ADJUSTMENT = 16
        self.LINE_NUMBER_START_DISTANCE = 12
        self.CODE_START_DISTANCE = 32
        self.BACKGROUND_COLOUR = "#151718"
        self.CODE_HIGHLIGHT_COLOUR = "#F1E60D"
        self.NODE_NORMAL_COLOUR = "#A9B7C6"
        self.EDGE_COLOUR = "#FFFFFF"
        self.NUMBER_COLOUR = "#6897BB"
        self.KEYWORD_COLOUR = "#CC7832"
        self.STRING_COLOUR = "#6A8759"
        self.FUNCTION_COLOUR = "#DCDCAA"
        self.NORMAL_COLOUR = "#A9B7C6"
        self.BOOLEAN_COLOUR = "#569CD6"
        self.LINE_COLOUR = "#858585"
        self.HIGHLIGHT_COLOUR = "#AEF359"
        self.STYLESHEET = NO_COPY + NORMAL_STYLE + " {}"
        self.last_code_highlight: int = -1

    def encode_image(self, image_str: str) -> img:
        print(image_str)
        byte_array = base64.b64encode(image_str.encode('utf-8'))
        return img(alt="", _class="img-responsive atto_image_button_text-bottom", style="object-fit:contain", width="100%", src="data:image/svg+xml;base64," + str(byte_array)[2:-1])

    def get_code_image(self, source: str) -> str:
        height, width = self._get_image_sizes(source)
        svg_tag: svg = svg(id="svg", width=width, height=height, viewBox="0.00 0.00 {} {}".format(width, height), xmlns="http://www.w3.org/2000/svg")
        svg_tag += defs(style(CDATA(self.STYLESHEET.format("")), type="text/css"))
        svg_tag += rect(fill=self.BACKGROUND_COLOUR, height=height, width=width, x=0, y=0)
        text_group = g(_class="normal", __pretty=False)
        svg_tag += text_group
        self._add_code_text(text_group, source)
        return svg_tag.render(pretty=False, xhtml=True)
        # byte_array = base64.b64encode(svg_tag.render(pretty=False, xhtml=True).encode('ascii'))
        # return str(byte_array)[2:-1]

    def _add_code_text(self, text_group: g, source: str) -> int:
        raise Exception("This functionality has not yet been implemented")

    def get_flowchart_image(self, source: str) -> str:
        nodes, edges = self.flow.parse_source(source)
        return self.dot_to_svg_string(self._generate_flowchart_dot_string(nodes, edges))
        # byte_array = base64.b64encode(self.dot_to_svg_string(self._generate_flowchart_dot_string(nodes, edges)).encode('ascii'))
        # return str(byte_array)[2:-1]
    
    def get_flowchart_image_mod(self, nodes, edges) -> img:
        # nodes, edges = self.flow.parse_source(source)
        # print(nodes)
        # print(edges)
        byte_array = base64.b64encode(self.dot_to_svg_string(self._generate_flowchart_dot_string_mod(nodes, edges)).encode('ascii'))
        return img(alt="", _class="img-responsive atto_image_button_text-bottom", style="object-fit:contain", width="100%", src="data:image/svg+xml;base64," + str(byte_array)[2:-1])

    def _generate_flowchart_dot_string(self, nodes: Dict[int, str], edges: Dict[Edge, str]) -> str:
        graph: str = 'digraph G {{\n\tgraph [bgcolor="{}", nodesep ="0.1" ];\n\t{{rank = min "0";}}\n\t{{rank = max "{}" }}'.format(self.BACKGROUND_COLOUR, -1)
        for i, n in nodes.items():
            node_style: str = ""
            if n == "Assignment" or n == "Function Call":
                node_style = 'shape="rect", style="filled", fillcolor="{}"'.format(self.NODE_NORMAL_COLOUR)
            elif n == "IO":
                node_style = 'shape="parallelogram", margin=0, style="filled", fillcolor="{}"'.format(self.NODE_NORMAL_COLOUR)
            elif n == "If" or n == "While":
                node_style = 'shape="diamond", style="filled", fillcolor="{}"'.format(self.NODE_NORMAL_COLOUR)
            else:
                node_style = 'shape="rect", style="rounded,filled", fillcolor="{}"'.format(self.NODE_NORMAL_COLOUR)
            if n == "Start" or n == "End":
                graph = graph + '\n\t"{0}" [label = "{1}",{2}, class="line{0}"];'.format(i, n, node_style)
            else:
                graph = graph + '\n\t"{0}" [label = "{0}: {1}",{2}, class="line{0}"];'.format(i, n, node_style)
        for s, e in edges:
            bits = edges[(s, e)].split("\n")
            if len(bits) == 1:
                graph = graph + '\n\t"{}" -> "{}" [label = <<table cellpadding="5" border="0" cellborder="0"><tr><td>{}</td></tr></table>>,color ="#ffffff",fontcolor = "#ffffff"];'.format(s, e, edges[(s, e)])
            else:
                graph = graph + '\n\t"{}" -> "{}" [label = <<table cellpadding="5" border="0" cellborder="0"><tr><td>{}</td></tr><tr><td>{}</td></tr></table>>,color ="#ffffff",fontcolor = "#ffffff"];'.format(s, e, bits[0], bits[1])
        graph = graph + "\n}"
        return graph

    def _generate_flowchart_dot_string_mod(self, nodes: Dict[str, List[str]], edges: Dict[str, str]) -> str:
        graph: str = 'digraph G {{\n\tgraph [bgcolor="{}", nodesep ="0.1" ];\n\t{{rank = min "0";}}\n\t{{rank = max "{}" }}'.format(self.BACKGROUND_COLOUR, -1)
        for i, n in nodes.items():
            node_style: str = ""
            if n[0] == "Assignment" or n == "Function Call":
                node_style = 'shape="rect", style="filled", fillcolor="{}"'.format(self.NODE_NORMAL_COLOUR)
            elif n[0] == "IO":
                node_style = 'shape="parallelogram", margin=0, style="filled", fillcolor="{}"'.format(self.NODE_NORMAL_COLOUR)
            elif n[0] == "If" or n == "While":
                node_style = 'shape="diamond", style="filled", fillcolor="{}"'.format(self.NODE_NORMAL_COLOUR)
            else:
                node_style = 'shape="rect", style="rounded,filled", fillcolor="{}"'.format(self.NODE_NORMAL_COLOUR)
            if n[0] == "Start" or n[0] == "End":
                graph = graph + '\n\t"{0}" [label = "{1}",{2}, class="line{0}"];'.format(i, n[1], node_style)
            else:
                graph = graph + '\n\t"{0}" [label = "{0}: {1}",{2}, class="line{0}"];'.format(i, n[1], node_style)
        for key in edges:
            ends = key.split("->")
            s = ends[0]
            e = ends[1]
            bits = edges[key].split("\n")
            if len(bits) == 1:
                graph = graph + '\n\t"{}" -> "{}" [label = <<table cellpadding="5" border="0" cellborder="0"><tr><td>{}</td></tr></table>>,color ="#ffffff",fontcolor = "#ffffff"];'.format(s, e, edges[key])
            else:
                graph = graph + '\n\t"{}" -> "{}" [label = <<table cellpadding="5" border="0" cellborder="0"><tr><td>{}</td></tr><tr><td>{}</td></tr></table>>,color ="#ffffff",fontcolor = "#ffffff"];'.format(s, e, bits[0], bits[1])
        graph = graph + "\n}"
        return graph

    def get_ast_image(self, code: Statement) -> str:
        labels: List[Tuple[str, str]] = list()
        edges: List[Tuple[str, str, str]] = list()
        self.get_labels_statement(code, labels, edges)
        dot_string = self._generate_ast_dot_string(labels, edges)
        return self.dot_to_svg_string(dot_string)
        # byte_array = base64.b64encode(self.dot_to_svg_string(dot_string).encode('ascii'))
        # return img(alt="", _class="img-responsive atto_image_button_text-bottom", style="object-fit:contain", width="100%", src="data:image/svg+xml;base64," + str(byte_array)[2:-1])

    def _generate_ast_dot_string(self, labels: List[Tuple[str, str]], edges: List[Tuple[str, str, str]]) -> str:
        label_str: str = ""
        for n, l in labels:
            label_str += "{} {}, fillcolor=\"{}\"];\n\t".format(n, l[0:-1], self.NODE_NORMAL_COLOUR)
        edge_str = ""
        if len(edges) > 0:
            edge_str = ";\n\t".join(["{} -> {} {}".format(*x) for x in edges]) + ";"
        dot_string = "digraph G {{ \n\tgraph [bgcolor=\"{}\"];\n\t".format(self.BACKGROUND_COLOUR) + label_str + edge_str + "\n}"
        return dot_string

    def get_code_animation(self, source: str) -> img:
        raise Exception("This functionality has not yet been implemented")
    
    def get_ast_animation(self, code: Statement) -> str:
        labels: List[Tuple[str, str]] = list()
        edges: List[Tuple[str, str, str]] = list()
        self.get_labels_statement(code, labels, edges)
        ast_svg_string = self.dot_to_svg_string(self._generate_ast_dot_string(labels, edges))
        ast_svg_xml = self.remove_xml_comments(parseString(ast_svg_string))
        key = self.generate_ast_animation_css([self.get_letter(i) for i in range(len(labels))], self.NODE_NORMAL_COLOUR, self.HIGHLIGHT_COLOUR, ast_svg_xml)
        flowchart_svg_tag = ast_svg_xml.getElementsByTagName("svg")[0]
        svg_defs_tag = ast_svg_xml.createElement("defs")
        cdata = ast_svg_xml.createCDATASection(key)
        style_tag = ast_svg_xml.createElement("style")
        style_tag.setAttribute("type", "text/css")
        flowchart_svg_tag.appendChild(svg_defs_tag)
        svg_defs_tag.appendChild(style_tag)
        style_tag.appendChild(cdata)
        pretty = self.pretty_xml(ast_svg_xml)
        return pretty
        # byte_array = base64.b64encode(pretty.encode('ascii'))
        # return img(alt="", _class="img-responsive atto_image_button_text-bottom", style="object-fit:contain", width="100%", src="data:image/svg+xml;base64," + str(byte_array)[2:-1])

    def get_all_animation(self, code: List[Statement], source_code: str) -> img:
        raise Exception("This functionality has not yet been implemented")

    def get_all_animation_list(self, code: List[Statement], source_code: str) -> List[str]:
        raise Exception("This functionality has not yet been implemented")

    def wrap_animation_list_html(self, svg_frames: Dict[int, str]):
        control_div = div()
        identifier = random.randint(0, 1000)
        control_div += img(id="image_{:03d}".format(identifier), alt="", _class="img-responsive atto_image_button_text-bottom", style="object-fit:contain", width="100%", src="")
        control_div += br()
        control_div += button("\u23EE Start", type="button", onclick="start_{:03d}()".format(identifier))
        control_div += button("\u23EA Back", type="button", onclick="back_{:03d}()".format(identifier))
        control_div += button("\u23F8 Pause", type="button", id="stopButton_{0:03d}".format(identifier), onclick="stop_{:03d}()".format(identifier))
        control_div += span("0", id="frame_num_{0:03d}".format(identifier))
        control_div += '/'
        control_div += span("0", id="frame_max_{0:03d}".format(identifier))
        control_div += button("Play \u23F5", type="button", id="playButton_{0:03d}".format(identifier), onclick="play_{0:03d}()".format(identifier))
        control_div += button("Forward \u23E9", type="button", onclick="forward_{0:03d}()".format(identifier))
        control_div += button("End \u23ED", type="button", onclick="end_{0:03d}()".format(identifier))
        control_div += scrpt(JS_TEMPLATE.format(identifier, str( [svg_frames[k] for k in sorted(svg_frames.keys()) ] )), type="text/javascript")
        return control_div

    def get_labels_statement(self, e: Statement, labels: List[Tuple[str, str]], edges: List[Tuple[str, str, str]]) -> None:
        label_string = '[shape="box", style="filled", label="{}\\n{}", class="node{}"]'
        edge_string = '[color ="{0}", dir="both", arrowhead="none", arrowtail="normal", label="{1}", fontcolor="{0}", class="edge{2}{3}"]'
        for s in e["calculation"]["subcalculations"]:
            self.get_labels_calculation(s, labels, edges)
        lab = self.get_letter(len(labels))
        e["calculation"]['fb_label'] = lab
        labels.append((lab, label_string.format(e["calculation"]["explanation"], e["calculation"]["code"].replace('"', '\\"'), lab)))
        for s in e["calculation"]["subcalculations"]:
            edges.append((lab, s['fb_label'], edge_string.format(self.EDGE_COLOUR, s["result_show"].replace('"', '\\"'), s['fb_label'], lab)))

    def get_labels_calculation(self, e: Calculation, labels: List[Tuple[str, str]], edges: List[Tuple[str, str, str]]) -> None:
        label_string = '[shape="box", style="filled", label="{}\\n{} => {}", class="node{}"]'
        edge_string = '[color ="{0}", dir="both", arrowhead="none", arrowtail="normal", label="{1}", fontcolor="{0}", class="edge{2}{3}"]'
        for s in e["subcalculations"]:
            self.get_labels_calculation(s, labels, edges)

        lab = self.get_letter(len(labels))
        e['fb_label'] = lab
        labels.append((lab, label_string.format(e["explanation"], e["code"].replace('"', '\\"'), e["result_show"].replace('"', '\\"'), lab)))
        for s in e["subcalculations"]:
            edges.append((lab, s['fb_label'], edge_string.format(self.EDGE_COLOUR, s["result_show"].replace('"', '\\"'), s['fb_label'], lab)))

    @staticmethod
    def get_letter(i: int) -> str:
        generated_name = ""
        while i > 25:
            generated_name = chr(ord('a') + i % 26) + generated_name
            i = i // 26
        generated_name = chr(ord('a') + i % 26) + generated_name
        return generated_name

    def _get_image_sizes(self, source: str):
        lines = [ln for ln in source.split('\n') if ln != ""]
        height = (len(lines) + 2) * self.LINE_SEPARATION
        width: float = 512
        lengths = [(len(line) + 4) * self.CHAR_WIDTH + self.CODE_START_DISTANCE * 2 for line in lines]
        if max(lengths) > width:
            width = max(lengths)
        return height, width

    @staticmethod
    def dot_to_svg_string(dot: str) -> str:
        src = Source(dot, format='svg')
        return src.pipe().decode('utf8')

    @staticmethod
    def calc_translation(st: Tuple[float, float], end: Tuple[float, float]) -> Tuple[float, float]:
        xt = st[0] - end[0]
        yt = st[1] - end[1]
        return xt, yt

    @staticmethod
    def parse_path_string(d: str) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        m, c = d.split("C")
        t = m[1:].split(",")
        end = (float(t[0]), float(t[1]))
        t = c.split(" ")[-1].split(",")
        start = (float(t[0]), float(t[1]))
        return start, end

    @staticmethod
    def percents_for_frame(frame_number: int, num_frames: int) -> Tuple[float, float, float, float]:
        block_size = 100 / num_frames
        if frame_number == 0:
            return 0, 0, (frame_number + 1) * block_size - 0.01, (frame_number + 1) * block_size
        elif frame_number == num_frames - 1:
            return frame_number * block_size, frame_number * block_size + 0.01, 100, 100
        else:
            return frame_number * block_size, frame_number * block_size + 0.01, (frame_number + 1) * block_size - 0.01, (frame_number + 1) * block_size

    def generate_keyframe(self, class_names: List[str], animation_name: str, frames: List[int], total_frames: int, attribute: str, value_on: str, value_off: str) -> str:
        if 0 not in frames:
            key = "@keyframes {0} {{ 0% {{ {1} : {2}; }} ".format(animation_name, attribute, value_off)
        else:
            key = "@keyframes {0} {{ ".format(animation_name)
        for frame_number in frames:
            a, b, c, d = self.percents_for_frame(frame_number, total_frames)
            key += "{0:.2f}% {{ {4} : {5}; }} {1:.2f}% {{ {4} : {6}; }}  {2:.2f}% {{ {4} : {6}; }} {3:.2f}% {{ {4} : {5}; }}".format(a, b, c, d, attribute, value_off, value_on)
        if total_frames - 1 not in frames:
            key += "100% {{ {} : {}; }} }}\n".format(attribute, value_off)
        else:
            key += "}\n"
        key += "{0} {{ animation: {1} {2}s linear infinite; }}\n".format(", ".join(class_names), animation_name, total_frames * 2)
        return key

    @staticmethod
    def get_edges(svg_tag: Element) -> List[Element]:
        groups = svg_tag.getElementsByTagName("g")
        edges = []
        for g in groups:
            c = g.getAttribute("class")
            if "edge" in c:
                name = c.split(" ")[-1]
                edges.append((name, g))
        return edges

    @staticmethod
    def percents_for_trans_frame(frame_number: int, num_frames: int) -> Tuple[float, float]:
        block_size = 100 / num_frames
        if frame_number == 0:
            return 0, (frame_number + 1) * block_size
        return frame_number * block_size, (frame_number + 1) * block_size

    def generate_trans_keyframe(self, class_name: str, animation_name: str, frame: int, total_frames: int, attribute: str, start_value: str, end_value: str) -> str:
        key = "@keyframes {0} {{ 0% {{ {1} : {2}; }} ".format(animation_name, attribute, start_value)
        a, b = self.percents_for_trans_frame(frame, total_frames)
        key += "{0:.2f}% {{ {2} : {3}; }}  {1:.2f}% {{ {2} : {4}; }}".format(a, b, attribute, start_value, end_value)
        key += "100% {{ {} : {}; }} }}\n".format(attribute, end_value)
        key += "{0} {{ animation: {1} {2}s linear infinite; }}\n".format(class_name, animation_name, total_frames * 2)
        return key

    def generate_ast_animation_css(self, node_list: List[str], node_colour: str, high_colour: str, svg_tag: Element) -> str:
        animation_frames = ""
        for i, l in enumerate(node_list):
            classes = [".node{} polygon".format(l)]
            animation_frames += self.generate_keyframe(classes, "node{}".format(l), [i + 1], len(node_list) + 2, "fill",
                                                       high_colour, node_colour)
        edges = sorted(self.get_edges(svg_tag))
        for i, et in enumerate(edges):
            n, e = et
            edge_path_svg_tag = e.getElementsByTagName("path")[0]
            path_string = edge_path_svg_tag.getAttribute("d")
            end, st = self.parse_path_string(path_string)
            edge_text_svg_tag = e.getElementsByTagName("text")[0]
            edge_text_svg_tag.setAttribute("text-anchor", "start")
            text_coord = (float(edge_text_svg_tag.getAttribute("x")), float(edge_text_svg_tag.getAttribute("y")))
            trs = self.calc_translation(st, text_coord)
            tre = self.calc_translation(end, text_coord)
            x = self.generate_trans_keyframe(".{} text".format(n), "mover{}".format(n), i + 1, len(edges) + 3, "transform", "translate({:.2f}px, {:.2f}px)".format(tre[0], tre[1]), "translate({:.2f}px, {:.2f}px)".format(trs[0], trs[1]))
            animation_frames += x
        return self.STYLESHEET.format(animation_frames)

    def remove_xml_comments(self, element: Element) -> Element:
        if isinstance(element, Comment):
            element.parentNode.removeChild(element)
        else:
            for subelement in element.childNodes[:]:
                self.remove_xml_comments(subelement)
        return element

    def _generate_animation_css(self, code_list: List[Statement], node_colour: str, high_colour: str) -> str:
        num_variables = len(code_list[-1]["variables_after"])
        lines = [int(x["current_line"]) for x in [empty_statement(0)] + deepcopy(code_list) + [empty_statement(-1)]]
        line_dict: Dict[int, List[int]] = {l: [] for l in set(lines)}
        animation_frames = ""
        for i, l in enumerate(lines):
            line_dict[l].append(i)
            classes = [".code_display{}".format(i)] + [".var_display{}_{}".format(i, x) for x in range(num_variables)]
            animation_frames += self.generate_keyframe(classes, "code{}".format(i), [i], len(lines), "visibility", "visible", "hidden")
        for l in sorted(line_dict.keys()):
            classes = [".line{0} polygon".format(l), ".line{0} path".format(l)]
            if l != -1:
                animation_frames += self.generate_keyframe(classes, "highlight_flow{}".format(l), sorted(line_dict[l]), len(lines), "fill", high_colour, node_colour)
                animation_frames += self.generate_keyframe([".codeline{0}".format(l)], "highlight_code{}".format(l), sorted(line_dict[l]), len(lines), "visibility", "visible", "hidden")
            else:
                animation_frames += self.generate_keyframe(classes, "highlight_flow{}".format(self.last_code_highlight), sorted(line_dict[l]), len(lines), "fill", high_colour, node_colour)
                animation_frames += self.generate_keyframe([".codeline{0}".format(self.last_code_highlight)], "highlight_code{}".format(self.last_code_highlight), sorted(line_dict[l]), len(lines), "visibility", "visible", "hidden")
        return self.STYLESHEET.format(animation_frames)

    def _generate_animation_css_list(self, code_list: List[Statement], node_colour: str, high_colour: str) -> Dict[int, str]:
        num_variables = len(code_list[-1]["variables_after"])
        lines = [int(x["current_line"]) for x in [empty_statement(0)] + deepcopy(code_list) + [empty_statement(-1)]]
        frames_dict: Dict[int, int] = {}
        frames_css_dict: Dict[int, str] = {}
        for i, l in enumerate(lines):
            frames_dict[i] = l
        for frame in sorted(frames_dict.keys()):
            classes = [".code_display{}".format(frame), ".codeline{0}".format(frames_dict[frame]) ] + [".var_display{}_{}".format(frame, x) for x in range(num_variables)]
            frames_css_dict[frame] = ".line{0} polygon, .line{0} path {{ fill : {1} }} {2} {{ visibility : visible }}".format(frames_dict[frame], high_colour, ", ".join(classes))
        return frames_css_dict

    @staticmethod
    def pretty_xml(xml: Element) -> str:
        return ''.join([line for line in xml.toprettyxml(indent='').split('\n') if line.strip()])
        return '\n'.join([line for line in xml.toprettyxml(indent='  ').split('\n') if line.strip()])

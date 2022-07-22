from typing import List, Set, Dict, Any
from dominate.tags import tr, td, table, th, div, h1, p, img, span, strong, br

from parser.parser_types import Statement, Calculation
import constants as c
from parser.generic_flowchart import FlowchartCreator
from parser.generic_parser import Parser
from imagecreator.image_generator import ImageGenerator

from parser.parser_types import Edge
from builder.variables import VarInfoBuilder
from builder.feedback import FeedbackBuilder
from builder.extra_tags import *
from builder.calculations import CalculationBuilder
from icecream import ic
from collections import namedtuple

Config = namedtuple('Config', 'language qtype format name category only reduced constants')


class Builder(object):
    def __init__(self, parser: Parser, flow_parser: FlowchartCreator, image_gen: ImageGenerator, config: Config, code_list: List[Statement]) -> None:
        super().__init__()
        self.parser = parser
        self.image_gen = image_gen
        self.flow_parse = flow_parser
        self.v = VarInfoBuilder(parser)
        self.calc = CalculationBuilder(parser, config.reduced, config.constants, code_list, self.v)
        self.fback = FeedbackBuilder(image_gen, config)

    def build_question(self, question_name: str, question_text: questiontext, tags: List[str]) -> question:
        quest = question(type="cloze")
        quest.add(name(text(question_name)))
        quest.add(penalty("0"))
        quest.add(hidden("0"))
        quest.add(question_text)
        tg = tgs()
        quest.add(tg)
        for t in tags:
            tg.add(tag(questiontextT(t)))
        return quest

    def build_line_div(self, code: Statement) -> div:
        line_div = div(
            style="display: flex; flex-direction: column; min-height: 100px; width:100%; float:left; padding: 10px")
        line_div.add(div(h1("Line Numbers")))
        line_table = table(width="100%")
        next_line = code["next_line"]

        wrong_lines = self.calc.get_lines() - set((next_line,))
        line_table.add(tr(td("Current Line:", style="border: 1px solid black"),
                          td(code["current_line"], style="border: 1px solid black"),
                          td("Next Line:", style="border: 1px solid black"),
                          td('{1:MCS:=' + next_line + "~" + "~".join(wrong_lines) + "}"), style="border: 1px solid black"))
        line_div.add(line_table)
        return line_div

    def build_intro_div_line(self, image_tag: img) -> div:
        intro_div = div(div(h1("Program Tracing Question:"),
                            p("Fill in the blanks or choose the correct option to show how the indicated line of code is executed."),
                            style="width:100%; "),
                        style="display: flex; flex-direction: column; min-height: 100px; width:100%; float:left; padding: 10px")
        intro_div.add(div(image_tag, style="width:100%"))
        return intro_div

    def build_intro_div_file(self, image_tag: img) -> div:
        intro_div = div(div(h1("Program Tracing Question:"),
                            p("Fill in the blanks or choose the correct option to show how the following code is executed."),
                            style="width:100%; "),
                        style="display: flex; flex-direction: column; min-height: 100px; width:100%; float:left; padding: 10px")
        intro_div.add(div(image_tag, style="width:100%"))
        return intro_div

    def build_question_text_line(self, code: Statement, image_tag: img, std_in: List[str]) -> question:
        question_text = questiontext()  # Wrapper for the whole of the question text, including encoded images
        actual_text = questiontextT()  # Where the html of the question text is recorded
        actual_text.add(self.build_intro_div_line(image_tag))
        if std_in and "".join(std_in) != "":
            actual_text.add(self.build_input_div(std_in))
        var_before, changes = self.v.get_symbol_tables(code)
        actual_text.add(self.build_line_div(code))
        actual_text.add(self.v.build_var_div_before(var_before))
        actual_text.add(self.calc.build_calc_div_line(code["calculation"]))
        actual_text.add(self.v.build_var_div_after(var_before, changes))
        question_text.add(actual_text)
        return question_text

    def build_input_div(self, std_in: List[str]) -> div:
        input_div = div(
            style="display: flex; flex-direction: column; min-height: 100px; width:100%; float:left; padding: 10px; border:1px solid black;")
        input_div.add(div(h1("User Input")))
        input_div.add(div(p("This section contains the user input of the whole program (if there is any). " +
                            "When an input function is called, the next line of text is returned as a result of the function. " +
                            "The return character (", span("⏎", style="font-size:30px"), ") is only to show where the end of a line of text is and is ", strong("not"), " returned by the function")))
        for i in std_in:
            input_div.add(span(i + "⏎", style="font-size:30px"), br())
        return input_div

    def build_question_text_file(self, code: List[Statement], image_tag: img, std_in: List[str]) -> question:
        question_text = questiontext()  # Wrapper for the whole of the question text, including encoded images
        actual_text = questiontextT()  # Where the html of the question text is recorded
        actual_text.add(self.build_intro_div_file(image_tag))
        if std_in and "".join(std_in) != "":
            actual_text.add(self.build_input_div(std_in))
        actual_text.add(self.calc.build_calc_div_file(code))
        question_text.add(actual_text)
        return question_text

    def build_line_questions(self, code_list: List[Statement], image: img, question_name: str, only_line_numbers: List[int], input_std: List[str]) -> List[question]:
        questions = []
        for i, statement in enumerate(code_list):
            if int(statement["current_line"]) in only_line_numbers or len(only_line_numbers) == 0:
                feedback = self.fback.build_feedback_line(statement)
                explanations = self.parser.get_all_explanations_statement(statement)
                tags = list(set([c.get_tag(x) for x in explanations]))
                tags.append("line " + str(statement["current_line"]))
                tags.append("Nodes " + str(self.count_statement_nodes(statement)))
                question_text = self.build_question_text_line(statement, image, input_std)
                qest = self.build_question("{}-{:02d}".format(question_name, i + 1), question_text, tags)
                qest.add(feedback)
                questions.append(qest)
        return questions

    def build_file_question(self, code_list: List[Statement], file_name: str, source_code: str, tags: List[str], std_in: str) -> List[question]:
        image = self.image_gen.get_code_image(source_code)
        img_tag = self.image_gen.encode_image(image)
        questions = []
        feedback = self.fback.build_feedback_file(code_list, source_code)
        question_text = self.build_question_text_file(code_list, img_tag, std_in)
        qest = self.build_question("{}".format(file_name.split("/")[-1]), question_text, tags)
        qest.add(feedback)
        questions.append(qest)
        return questions

    @staticmethod
    def create_quiz(cat: str) -> quiz:
        category_name = "$course$/top/" + cat
        quiz_root = quiz()
        quiz_root.add(question(category(text(category_name)), info(format="html"), type="category"))
        return quiz_root

    def count_statement_nodes(self, code: Statement) -> int:
        return 1 + sum([self.count_calculation_nodes(sc) for sc in code["calculation"]["subcalculations"]])

    def count_calculation_nodes(self, code: Calculation) -> int:
        return 1 + sum([self.count_calculation_nodes(sc) for sc in code["subcalculations"]])

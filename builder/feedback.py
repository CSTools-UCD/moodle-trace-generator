from typing import List, Dict
from imagecreator.image_generator import ImageGenerator
from parser.parser_types import Statement, Calculation, Edge
from builder.extra_tags import generalfeedback, questiontextT
from dominate.tags import div, p, ul, img, li, ul
from collections import namedtuple

Config = namedtuple('Config', 'language qtype format name category only reduced constants')


class FeedbackBuilder(object):
    def __init__(self, image_gen: ImageGenerator, con: Config) -> None:
        super().__init__()
        self.config: Config = con
        self.image_gen = image_gen

    def build_feedback_line(self, code: Statement) -> generalfeedback:
        feedback = generalfeedback(format="html")
        feedbackText = questiontextT()
        divHolder = div(style="width:100%")
        d = div(style="width:100%")
        if self.config.format == 'svg':
            image = self.image_gen.get_ast_animation(code)
            img_tag = self.image_gen.encode_image(image)
            d += p("The diagram above shows how this line of code is executed. The boxes are highlighted in green in the order that the operation contain in them are executed. The text below gives an explanation of this order.")
        else:
            image = self.image_gen.get_ast_image(code)
            img_tag = self.image_gen.encode_image(image)
            d += p("The diagram above shows how this line of code is executed. The text below gives an explanation of this order.")
        divHolder.add(img_tag)
        feedbackText.add(divHolder)

        listRoot = ul()
        self.add_statement_explaination(code, listRoot)
        d.add(listRoot)
        feedbackText.add(d)
        feedback.add(feedbackText)
        return feedback

    def build_feedback_file(self, code: List[Statement], source_code: str) -> generalfeedback:
        feedback = generalfeedback(format="html")
        feedbackText = questiontextT()
        divHolder = div(style="width:100%")
        feedbackText.add(divHolder)
        d = div(style="width:100%")
        if self.config.format == 'svg':
            image = self.image_gen.get_all_animation(code, source_code)
            img_tag = self.image_gen.encode_image(image)
            divHolder.add(img_tag)
            para = p(
                "The diagram above shows an animation of the overall program flow. On the left, the flowchart shows the control flow of the program and on the right the code is being shown. The line of code and the corresponding part of the flowchart are highlighted step by step to show the execution of the program. The table below the code shows the currently executing line of code as well as the current value of each of the variables.")
            d.add(para)
        elif self.config.format == 'html':
            image_div: div = self.image_gen.get_all_animation_list(code, source_code)
            # image_tag = self.image_gen.encode_image(image)
            divHolder.add(image_div)
            para = p(
                "The diagram above shows an animation of the overall program flow. On the left, the flowchart shows the control flow of the program and on the right the code is being shown. The line of code and the corresponding part of the flowchart are highlighted step by step to show the execution of the program. The table below the code shows the currently executing line of code as well as the current value of each of the variables.")
            d.add(para)
        else:
            image = self.image_gen.get_flowchart_image(source_code)
            img_tag = self.image_gen.encode_image(image)
            divHolder.add(img_tag)
            para = p(
                "The flowchart above shows the control flow of the executed code. The program executes following the arrows from start to end. At condition statements (diamond) there are multiple choices and the correct one will be chosen based on the condition.")
            d.add(para)

        listRoot = ul()
        d.add(listRoot)
        feedbackText.add(d)
        feedback.add(feedbackText)
        return feedback

    def add_statement_explaination(self, code: Statement, unorderedList: ul) -> None:
        message = "The main operation on this line is " + code["calculation"]["explanation"].lower() + ". "
        message += code["calculation"]["calculation_explanation"]
        explanationItem = li(message)
        unorderedList.add(explanationItem)
        if len(code["calculation"]["subcalculations"]) > 0:
            subList = ul()
            for child in code["calculation"]["subcalculations"]:
                self.add_calculation_explaination(child, subList)
            explanationItem.add(subList)

    def add_calculation_explaination(self, code: Calculation, unorderedList: ul) -> None:
        message = "Before we can complete the above operation, we must comlete this. This operation is " + code["explanation"].lower() + ". "
        message += code["calculation_explanation"]
        explanationItem = li(message)
        unorderedList.add(explanationItem)
        if len(code["subcalculations"]) > 0:
            subList = ul()
            for child in code["subcalculations"]:
                self.add_calculation_explaination(child, subList)
            explanationItem.add(subList)

import base64
from typing import Dict
from flask import Flask, render_template, request, jsonify, send_file
import os
from io import BytesIO
import json
import zipfile

from parser.generic_flowchart import FlowchartCreator
from parser.generic_parser import Parser
from imagecreator.image_generator import ImageGenerator

import parser.python.parser as python_parser
import parser.python.flowchart as python_flow_parser
import imagecreator.python_generator as python_image_gen
import parser.c.parser as c_parser
import parser.c.flowchart as c_flow_parser
import imagecreator.c_generator as c_image_gen

from builder.builder import Builder
from builder.extra_tags import quiz
from typing import List, Dict
import parser.multiplier as template_generator
import constants as c
import imagecreator.c_generator as c_gen
import imagecreator.python_generator as py_gen
import parser.c.flowchart as c_flowchart
import parser.c.parser as c_parser
import parser.python.parser as py_parser
import parser.python.flowchart as py_flowchart
from collections import namedtuple

app = Flask(__name__)
Config = namedtuple('Config', 'language qtype format name category only reduced constants')
preface = ""

@app.route('/quiz/', methods=['GET'])
def main_page():
    return render_template('main.html', preface=preface)

@app.route('/quiz/create/', methods=['GET'])
def trace_form():
    return render_template('trace-form.html', preface=preface)

@app.route('/quiz/advanced/', methods=['GET'])
def advanced_trace_form():
    return render_template('advanced-form.html', preface=preface)

@app.route('/quiz/examples/', methods=['GET'])
def quiz_examples():
    return render_template('trace-examples.html', preface=preface)

@app.route('/quiz/create/', methods=['POST'])
def process_quiz_post(): 
    os.makedirs("temp", exist_ok=True)
    if request.method == 'POST':
        language = request.form['language']
        frmat = request.form['format']
        code_file = None
        input_file = None
        files = {}
        if "code" in request.files:
            code_file = request.files['code']
            files['code'] = code_file.stream.read().decode("utf-8")
        if "input" in request.files:
            input_file = request.files['input']
            files['input'] = input_file.stream.read().decode("utf-8")
        question_name = request.form['qname']
        category_name = request.form['cat']
        question_type = request.form['type']
        only_lines = request.form['only']
        reduced_questions = 'reduced' in request.form
        display_constants = 'cons' in request.form
        cfg = Config(language, question_type, frmat, question_name, category_name, only_lines, reduced_questions, display_constants)
        quiz_str = process(cfg, files)
        buffer = BytesIO()
        buffer.write(quiz_str.encode("utf-8"))
        buffer.seek(0)
        return send_file(
            buffer, 
            as_attachment=True,
            download_name='questions.xml',
            mimetype='text/xml'
        )
    else:
        return jsonify("{\"error\" : \"was not a post\"}")

@app.route('/quiz/advanced/', methods=['POST'])
def process_advanced_quiz_post(): 
    os.makedirs("temp", exist_ok=True)
    if request.method == 'POST':
        language = request.form['language']
        frmat = request.form['format']
        code_file = None
        param_file = None
        input_file = None
        files = {}
        if "code" in request.files:
            code_file = request.files['code']
            files['code'] = code_file.stream.read().decode("utf-8")
        if "param" in request.files:
            param_file = request.files['param']
            files['param'] = param_file.stream.read().decode("utf-8")
        if "input" in request.files:
            input_file = request.files['input']
            files['input'] = input_file.stream.read().decode("utf-8")
        question_name = request.form['qname']
        category_name = request.form['cat']
        question_type = request.form['type']
        only_lines = request.form['only']
        reduced_questions = 'reduced' in request.form
        display_constants = 'cons' in request.form
        cfg = Config(language, question_type, frmat, question_name, category_name, only_lines, reduced_questions, display_constants)
        quiz_str = process(cfg, files)
        buffer = BytesIO()
        buffer.write(quiz_str.encode("utf-8"))
        buffer.seek(0)
        return send_file(
            buffer, 
            as_attachment=True,
            download_name='questions.xml',
            mimetype='text/xml'
        )
        return 
    else:
        return jsonify("{\"error\" : \"was not a post\"}")


@app.route('/images/create/', methods=['GET'])
def image_form():
    return render_template('image-form.html', preface=preface)

@app.route('/images/examples/', methods=['GET'])
def image_examples():
    return render_template('image-examples.html', preface=preface)

@app.route('/images/create/', methods=['POST'])
def process_image_post(): 
    os.makedirs("temp", exist_ok=True)
    if request.method == 'POST':
        language = request.form['language']
        content = request.form['content']
        frmat = request.form['format']
        file = request.files["file"]

        if not file or not language or not content:
            flash('Required information is missing')
            return jsonify("{\"error\" : \"Required information is missing\"}")
        
        code = file.stream.read().decode("utf-8")
        
        if language == 'python':
            parser = py_parser.PythonParser()
            img_gen = py_gen.PythonImageGenerator(py_flowchart.PythonFlowCreator())
        else:
            parser = c_parser.CParser()
            img_gen = c_gen.CImageGenerator(c_flowchart.CFlowCreator())

        if content == "flowchart":
            return_image = img_gen.get_flowchart_image(code)
            return return_single_image(return_image)
        elif content == "code":
            return_image = img_gen.get_code_image(code)
            return return_single_image(return_image)
        elif content == "both":
            code_list, line_numbers = parser.parse_source(code)
            if frmat and frmat == "svg":
                return_image = img_gen.get_all_animation(code_list, code)
                return return_single_image(return_image)
            elif frmat and frmat == "html":
                images = img_gen.get_all_animation_list(code_list, code)
                div_tag = img_gen.wrap_animation_list_html(images)
                return return_html_page(str(div_tag))
            elif frmat and frmat == "zip":
                return_images = img_gen.get_all_animation_list(code_list, code)
                return return_zip_file(return_images)
    return jsonify("{ 'error' : 'An error has occurred'}")

def return_single_image(val: str) -> send_file:
    buffer = BytesIO()
    buffer.write(val.encode("utf-8"))
    buffer.seek(0)
    return send_file(
        buffer, 
        as_attachment=True,
        download_name='image.svg',
        mimetype='image/svg+xml'
    )

def return_html_page(html_str: str) -> send_file:
    buffer = BytesIO()
    buffer.write(html_str.encode("utf-8"))
    buffer.seek(0)
    return send_file(
        buffer, 
        as_attachment=True,
        download_name='frames.html',
        mimetype='text/html'
    )

def return_zip_file(image_list: Dict[int, str]) -> send_file:
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for i, image in image_list.items():
            decode = base64.b64decode(image.encode('ascii'))
            zip_file.writestr("{:02d}.svg".format(int(i)), decode)

    zip_buffer.seek(0)
    return send_file(
        zip_buffer, 
        as_attachment=True,
        download_name='images.zip',
        mimetype='application/zip'
    )

def generate_templated_code_question(
                q_root: quiz, 
                parser: Parser, 
                flowchart_parser: FlowchartCreator, 
                image_generator: ImageGenerator, 
                config: Config, 
                files: Dict[str, str]):
    templated_codes = template_generator.generate_from_template(files['code'], files['param'], config.name)
    input_dict = {}
    if 'input' in files and files['input'] != '':
        json.loads(files['input'])
    num = 0
    for name, source_code in templated_codes:
        std_in = []
        if input_dict and str(num) in input_dict:
            std_in = input_dict[str(num)].split("\n")
            parser.set_input(std_in)
        code_list, line_numbers = parser.parse_source(source_code)
        builder = Builder(parser, flowchart_parser, image_generator, config, code_list)
        image = image_generator.get_code_image(source_code)
        img_tag = image_generator.encode_image(image)

        if config.qtype == 'individual' or config.qtype == 'both':
            only_line_numbers: List[int] = []
            if config.only:
                only_line_numbers = [int(x) for x in config.only.split(",")]
            questions = builder.build_line_questions(code_list, img_tag, name, only_line_numbers, std_in)
            for q in questions:
                q_root.add(q)
        if config.qtype == 'all' or config.qtype == 'both':
            explanations: List[str] = Parser.get_explanations_code(code_list)
            tags = list(set([c.get_tag(x) for x in explanations]))
            questions = builder.build_file_question(code_list, name, source_code, tags, std_in)
            for q in questions:
                q_root.add(q)
        num = num + 1

def generate_code_question(q_root: quiz, 
                        parser: Parser, 
                        flowchart_parser: FlowchartCreator, 
                        image_generator: ImageGenerator,
                        config: Config, 
                        files: Dict[str,str]):
    source_code = files['code']
    std_in = []
    if 'input' in files and files['input']:
        parser.set_input(files['input'].split("\n"))
    only_line_numbers: List[int] = []
    if config.only:
        only_line_numbers = [int(x) for x in config.only.split(",")]
    code_list, line_numbers = parser.parse_source(source_code)
    builder = Builder(parser, flowchart_parser, image_generator, config, code_list)
    image = image_generator.get_code_image(source_code)
    img_tag = image_generator.encode_image(image)
    if config.qtype == 'individual' or config.qtype == 'both':
        questions = builder.build_line_questions(code_list, img_tag, config.name, only_line_numbers, std_in)
        for q in questions:
            q_root.add(q)
    if config.qtype == 'all' or config.qtype == 'both':
        explanations: List[str] = Parser.get_explanations_code(code_list)
        tags = list(set([c.get_tag(x) for x in explanations]))
        questions = builder.build_file_question(code_list, config.name, source_code, tags, std_in)
        for q in questions:
            q_root.add(q)

def process(con : Config, files: Dict[str, str]):
    code_parser: Parser = None
    flow_parser: FlowchartCreator = None
    image_gen: ImageGenerator = None
    if con.language == 'python':
        code_parser = python_parser.PythonParser()
        flow_parser = python_flow_parser.PythonFlowCreator()
        image_gen = python_image_gen.PythonImageGenerator(flow_parser)
    elif con.language == "c":
        code_parser = c_parser.CParser()
        flow_parser = c_flow_parser.CFlowCreator()
        image_gen = c_image_gen.CImageGenerator(flow_parser)
    else:
        raise Exception("This language has not been implemented yet")
    quiz_root = Builder.create_quiz(con.category)
    print(files)
    if 'param' in files:
        generate_templated_code_question(quiz_root, code_parser, flow_parser, image_gen, con, files)
    else:
        generate_code_question(quiz_root, code_parser, flow_parser, image_gen, con, files)

    return str(quiz_root)
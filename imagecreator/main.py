import argparse
import os
import json

from imagecreator.python_generator import PythonImageGenerator
from parser.python.flowchart import PythonFlowCreator

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description='Generating code tracing quiz questions for moodle')
    arg_parser.add_argument("codefile", help="This is the Python code file you want to generate a tracing quiz for", type=str)
    arguments = arg_parser.parse_args()
    
    

    arg_code_file = arguments.codefile
    if not os.path.exists(arg_code_file):
        print("codefile must point to a readable file")
        quit()

    source = open(arg_code_file,"r").read()
    gen = PythonImageGenerator(PythonFlowCreator())
    # img1 = gen.get_code_image(source)
    # # print(img1)

    # img2 = gen.get_flowchart_image(source)
    # print(img2)

    both = json.load(open(arg_code_file,"r"))
    nodes = both["nodes"]
    edges = both["edges"]
    img3 = gen.get_flowchart_image_mod(nodes, edges)
    # print(img3)
from parser.c.flowchart import CFlowCreator
from imagecreator.python_generator import PythonImageGenerator
from imagecreator.c_generator import CImageGenerator
from parser.python.flowchart import PythonFlowCreator
from parser.python.parser import PythonParser
from parser.c.parser import CParser

if __name__ == "__main__":
    p = True
    if p:
        source = 'd = [1,2,3]\nv = 0\nwhile v < 3:\n    d[v] = d[v] *3\n    v = v + 1'
        gen = PythonImageGenerator(PythonFlowCreator())
        img1 = gen.get_code_image(source)
        # print(img1)
        # img2 = gen.get_flowchart_image(source)
        # print(img2)

        # pp = PythonParser()
        # pp.set_input(["54"])
        # code_list, line_numbers = pp.parse_source(source)
        # img3 = gen.get_ast_image(code_list[1])
        # print(img3)

        # img4 = gen.get_ast_animation(code_list[1])
        # print(img4)

        # img5 = gen.get_all_animation(code_list, source)
        # print(img5)
    c = False
    if c:
        source = 'int main(){\n    int numbers[3] = {5,6,2};\n    int i = 0;\n    while (i < 3){\n        numbers[i] = numbers[i] * 2;\n        i = i + 1;\n    }\n}\n'
        # source = 'int main(){\n\tint x = 0;\n\twhile (x < 5){\n\t\tprintf("%d",x);\n\t\tx = x + 1;\n\t}\n}\n'
        gen = CImageGenerator(CFlowCreator())
        # img1 = gen.get_code_image(source)
        # print(img1)

        # img2 = gen.get_flowchart_image(source)
        # print(img2)

        cp = CParser()
        # cp.set_input(["54"])
        code_list, line_numbers = cp.parse_source(source)
        # img3 = gen.get_ast_image(code_list[1])
        # print(img3)

        # img4 = gen.get_ast_animation(code_list[1])
        # print(img4)

        img5 = gen.get_all_animation(code_list, source)
        # print(img5)

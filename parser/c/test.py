from parser.c.flowchart import CFlowCreator
from imagecreator.c_generator import CImageGenerator
from parser.c.parser import CParser
import json

if __name__ == "__main__":
    source = 'int main(){\n    int x;\n    scanf("%d",&x);\n    if (x > 40){\n        printf("%d",y);\n    }\n}\n'
    source = 'int main(){\n\tint x = 0;\n\tif (!(x > 50)){\n\t\tprintf("%d",x);\n\t\tx = x + 1;\n\t}\n}\n'
    gen = CImageGenerator(CFlowCreator())
    # img1 = gen.get_code_image(source)
    # print(img1)
    #
    # img2 = gen.get_flowchart_image(source)
    # print(img2)

    cp = CParser()
    cp.set_input(["54"])
    code_list, line_numbers = cp.parse_source(source)
    # print(json.dumps(code_list))
    img3 = gen.get_ast_image(code_list[1])
    print(img3)
    #
    img4 = gen.get_ast_animation(code_list[1])
    print(img4)
    #
    img5 = gen.get_all_animation(code_list, source)
    print(img5)
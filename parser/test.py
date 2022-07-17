from typing import List, Set, Dict, Tuple, Optional, Any
from parser.parser_types import Statement
from parser.python_parser import parse_file
import unittest
import json
file_base = "./testing/"
class TestParsingMethods(unittest.TestCase):

    def test_basic(self)-> None:
        test_file = file_base + "01.py"
        result_file = file_base + "01.json"
        code_list, line_numbers = parse_file(test_file)
        parsed = json.dumps(code_list, sort_keys=True, indent=2)
        f = open(result_file, "r")
        r = json.load(f)
        f.close()
        result = json.dumps(r, sort_keys=True, indent=2)
        self.assertEqual(parsed, result)
        

    def test_binary_math_int(self)-> None:
        test_file = file_base + "02.py"
        result_file = file_base + "02.json"
        code_list, line_numbers = parse_file(test_file)
        parsed = json.dumps(code_list, sort_keys=True, indent=1)

        f = open(result_file, "r")
        r = json.load(f)
        f.close()
        result = json.dumps(r, sort_keys=True, indent=1)
        self.assertEqual(parsed, result)

    def test_binary_str(self)-> None:
        test_file = file_base + "03.py"
        result_file = file_base + "03.json"
        code_list, line_numbers = parse_file(test_file)
        parsed = json.dumps(code_list, sort_keys=True, indent=1)
        f = open( file_base +"03o.json", "w")
        f.write(parsed)
        f.close()
        f = open(result_file, "r")
        r = json.load(f)
        result = json.dumps(r, sort_keys=True, indent=1)
        f.close()
        self.assertEqual(parsed, result)

    def test_binary_bool(self)-> None:
        test_file = file_base + "04.py"
        result_file = file_base + "04.json"
        code_list, line_numbers = parse_file(test_file)
        parsed = json.dumps(code_list, sort_keys=True, indent=1)
        f = open( file_base +"04o.json", "w")
        f.write(parsed)
        f.close()
        f = open(result_file, "r")
        r = json.load(f)
        result = json.dumps(r, sort_keys=True, indent=1)
        f.close()
        self.assertEqual(parsed, result)

    def test_binary_math_float(self)-> None:
        test_file = file_base + "05.py"
        result_file = file_base + "05.json"
        code_list, line_numbers = parse_file(test_file)
        parsed = json.dumps(code_list, sort_keys=True, indent=1)
        f = open( file_base +"05o.json", "w")
        f.write(parsed)
        f.close()
        f = open(result_file, "r")
        r = json.load(f)
        f.close()
        result = json.dumps(r, sort_keys=True, indent=1)
        self.assertEqual(parsed, result)

    def test_if(self)-> None:
        test_file = file_base + "06.py"
        result_file = file_base + "06.json"
        code_list, line_numbers = parse_file(test_file)
        parsed = json.dumps(code_list, sort_keys=True, indent=1)
        f = open( file_base +"06o.json", "w")
        f.write(parsed)
        f.close()
        f = open(result_file, "r")
        r = json.load(f)
        f.close()
        result = json.dumps(r, sort_keys=True, indent=1)
        self.assertEqual(parsed, result)

    def test_comparisons(self)-> None:
        test_file = file_base + "07.py"
        result_file =file_base + "07.json"
        code_list, line_numbers = parse_file(test_file)
        parsed = json.dumps(code_list, sort_keys=True, indent=1)
        f = open( file_base +"07o.json", "w")
        f.write(parsed)
        f.close()
        f = open(result_file, "r")
        r = json.load(f)
        f.close()
        result = json.dumps(r, sort_keys=True, indent=1)
        self.assertEqual(parsed, result)

    def test_while(self)-> None:
        test_file = file_base + "08.py"
        result_file = file_base + "08.json"
        code_list, line_numbers = parse_file(test_file)
        parsed = json.dumps(code_list, sort_keys=True, indent=1)
        f = open( file_base +"08o.json", "w")
        f.write(parsed)
        f.close()
        f = open(result_file, "r")
        r = json.load(f)
        f.close()
        result = json.dumps(r, sort_keys=True, indent=1)
        self.assertEqual(parsed, result)

    def test_func_call(self)-> None:
        test_file = file_base + "09.py"
        result_file = file_base + "09.json"
        code_list, line_numbers = parse_file(test_file)
        parsed = json.dumps(code_list, sort_keys=True, indent=1)
        f = open( file_base +"09o.json", "w")
        f.write(parsed)
        f.close()
        f = open(result_file, "r")
        r = json.load(f)
        f.close()
        result = json.dumps(r, sort_keys=True, indent=1)
        self.assertEqual(parsed, result)

    def test_more_func_call(self)-> None:
        test_file = file_base + "10.py"
        result_file = file_base + "10.json"
        code_list, line_numbers = parse_file(test_file)
        parsed = json.dumps(code_list, sort_keys=True, indent=1)
        f = open( file_base +"10o.json", "w")
        f.write(parsed)
        f.close()
        f = open(result_file, "r")
        r = json.load(f)
        f.close()
        result = json.dumps(r, sort_keys=True, indent=1)
        self.assertEqual(parsed, result)

    def test_multi_str(self)-> None:
        test_file = file_base + "11.py"
        result_file = file_base + "11.json"
        code_list, line_numbers = parse_file(test_file)
        parsed = json.dumps(code_list, sort_keys=True, indent=1)
        f = open( file_base +"11o.json", "w")
        f.write(parsed)
        f.close()
        # f = open(result_file, "r")
        # r = json.load(f)
        # f.close()
        # result = json.dumps(r, sort_keys=True, indent=1)
        # self.assertEqual(parsed, result)


    def test_multi_lst(self)-> None:
        test_file = file_base + "12.py"
        result_file = file_base + "12.json"
        code_list, line_numbers = parse_file(test_file)
        parsed = json.dumps(code_list, sort_keys=True, indent=1)
        f = open( file_base +"12o.json", "w")
        f.write(parsed)
        f.close()
        # f = open(result_file, "r")
        # r = json.load(f)
        # f.close()
        # result = json.dumps(r, sort_keys=True, indent=1)
        # self.assertEqual(parsed, result)

    def test_complex_str(self)-> None:
        test_file = file_base + "13.py"
        result_file = file_base + "13.json"
        code_list, line_numbers = parse_file(test_file)
        parsed = json.dumps(code_list, sort_keys=True, indent=1)
        f = open( file_base +"13o.json", "w")
        f.write(parsed)
        f.close()
        # f = open(result_file, "r")
        # r = json.load(f)
        # f.close()
        # result = json.dumps(r, sort_keys=True, indent=1)
        # self.assertEqual(parsed, result)

    def test_complex_str2(self)-> None:
        test_file = file_base + "14.py"
        result_file = file_base + "14.json"
        code_list, line_numbers = parse_file(test_file)
        parsed = json.dumps(code_list, sort_keys=True, indent=1)
        f = open( file_base +"14o.json", "w")
        f.write(parsed)
        f.close()
        # f = open(result_file, "r")
        # r = json.load(f)
        # f.close()
        # result = json.dumps(r, sort_keys=True, indent=1)
        # self.assertEqual(parsed, result)

    def test_complex_elif(self)-> None:
        test_file = file_base + "15.py"
        # result_file = file_base + "15.json"
        code_list, line_numbers = parse_file(test_file)
        parsed = json.dumps(code_list, sort_keys=True, indent=1)
        f = open( file_base +"15o.json", "w")
        f.write(parsed)
        f.close()
        # f = open(result_file, "r")
        # r = json.load(f)
        # f.close()
        # result = json.dumps(r, sort_keys=True, indent=1)
        # self.assertEqual(parsed, result)

if __name__ == "__main__":
    unittest.main()
from typing import Tuple, Dict
from parser.parser_types import Edge

class FlowchartCreator(object):

    def __init__(self) -> None:
        super().__init__()
        self.flow_nodes : Dict[int, str] = {}
        self.flow_edges : Dict[Edge, str] = {}

    def parse_source(self, SOURCE : str) -> Tuple[Dict[int, str], Dict[Edge, str]]:
        pass
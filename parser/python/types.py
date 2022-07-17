from typing import Set

INT = "int"
FLOAT = "float"
STRING = "str"
BOOLEAN = "bool"
LIST = "list"
NONE = "None"

types: Set[str] = {INT, STRING, FLOAT, BOOLEAN, LIST, NONE}


def getWrongTypes(ans: str) -> Set[str]:
    return types - set((ans,))

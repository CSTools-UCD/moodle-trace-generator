from typing import Set

c_types_size = {"char": 1, "short": 2, "int": 4, "long": 8, "double": 8}
c_types_max = {"char": 255, "short": 32767, "int": 2147483647, "long": 9223372036854775807}
c_types_min = {"char": 0, "short": -32768, "int": -2147483648, "long": -9223372036854775808}

CHAR = "char"
SHORT = "short"
INT = "int"
LONG = "long"
FLOAT = "double"

STRING = "char[]"
BOOLEAN = "int"

types: Set[str] = {INT, CHAR, SHORT, LONG, FLOAT, STRING}


def getWrongTypes(ans: str) -> Set[str]:
    return types - set((ans,))


def is_integer(typ: str) -> bool:
    if typ in ("char", "int", "long", "short"):
        return True
    return False


def is_number(typ: str) -> bool:
    if typ in c_types_size:
        return True
    return False


def get_largest_type(lt: str, rt: str) -> str:
    if is_integer(lt) and is_integer(rt):
        if c_types_size[lt] >= c_types_size[rt]:
            return lt
        else:
            return rt
    elif is_integer(lt):
        return rt
    elif is_integer(rt):
        return lt
    else:
        if c_types_size[lt] >= c_types_size[rt]:
            return lt
        else:
            return rt

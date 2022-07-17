from typing import Set

""" These are for ensuring the length of the entry boxes """
WRONG = "13 characters"
V_WRONG = "1cters"
WRONG_NUM = "123456678:0.1"

""" These constants are for remembering the names of the operations in the language shown in the explanation box """
M_ASS = "Assignment"
M_FUN = "Function used"
M_VAR = "Value loaded from variable"
M_LOAD_LIST = "Value loaded from sequence"
M_LOAD_ARRAY = "Value loaded from array"
M_DEF_LIST = "Literal definition of list"
M_CONST = "Literal constant in code"
M_IF = "If statement condition check"
M_WHILE = "While statement condition check"
M_FIN = "Program Finished"

M_ADD = "Addition"
M_CON = "Concatenation"
M_SUB = "Subtraction"
M_MUL = "Multiplication"
M_REP = "Replication"
M_DIV = "Division"
M_IDIV = "Integer Division"
M_MOD = "Modulus"
M_EXP = "Exponent"

M_UADD = "Unary addition"
M_USUB = "Unary subtraction"
M_NOT = "Logical not"
M_BNOT = "Bitwise not"

M_EQC = "Equals comparison"
M_NEC = "Not equals comparison"
M_LTC = "Less than comparison"
M_LTE = "Less than or equals comparison"
M_GTC = "Greater than comparison"
M_GTE = "Greater than or equals comparison"

M_AND = "Logical And"
M_OR = "Logical Or"

""" These constants are for remembering the explanations given in the question feedback"""
EXP_WHILE = "This part of the code checks if the condition of the while statement True. If it is we will execute the body of the statement, if it is False we will execute the next statement. Before we can make this choice, we must know the value of the condition. So this calculation must be performed first. "
EXP_ASSIGN = "The operation of assignment is where the value on the right side is remembered by the program using the name on the left side of the equals sign. Before we can execute this operation, we must know the value of the right side."
EXP_IF = "This part of the code checks if the condition of the if statement True. If it is we will execute the body of the statement, if it is False we will execute the else component (if there is one) or the next statement. Before we can make this choice, we must know the value of the condition. So this must be evaluated first. "
EXP_CON = "A constant is a literal that value was included in the code, this can just be used in the expression/code without any more work. We do not need to do any more calculations for the value of this part of the expression to be known. "
EXP_LOAD = "This operation is were we find a value that the program has remembered before using it's name. The value is returned and we have no more work to do here."
EXP_LOAD_ARRAY = "This operation is were we find a value that the program has remembered in an array. We need to know the index of the value we want to load before we can get it."
EXP_FUNC = "This operation is calling a function. Before we can call the function, we must know the value of each of the parameters. This means that we must evaluate each of the parameters before the function can be called. The parameters will be evaluated from left to right. "

SUB_EXP_BOP = "Before we can calculate the result of this operation we must know the result of both operands (sides of the operation). The left side of the expression will be evaluated first, then the right side of the expression. "
SUB_EXP_UOP = "Before we can calculate the result of this operation we must know the result of the single operand. "

EXP_ADD = "The operation of addition. " + SUB_EXP_BOP
EXP_CAT = "The operation of concatenation (joining two strings together). " + SUB_EXP_BOP
EXP_SUB = "The operation of subtraction, the value of the right side will be subtracted from the left side. " + SUB_EXP_BOP
EXP_MULT = "The operation of multiplication. " + SUB_EXP_BOP
EXP_REP = "The operation of replication (a string [left] and a number [right]). " + SUB_EXP_BOP
EXP_DIV = "The operation of division, the value of the left side of the operation will be divided by the value of the right side. " + SUB_EXP_BOP
EXP_IDIV = "The operation of integer division (also called floor division), the value of the left side of the operation will be divided by the value of the right side, however the result will be rounded down to an integer value. " + SUB_EXP_BOP
EXP_MOD = "The operation of modulus division, this operation returns the remainder of an integer division of the left value by the right value. It is equivelant to (l - ( (l // r) * r). " + SUB_EXP_BOP
EXP_POW = "The operation of exponent, this calculates the left side to the power of the right side. " + SUB_EXP_BOP
EXP_AND = "The logical and operation takes a number boolean values and returns True if all of the values are True (False if they are not). " + SUB_EXP_BOP
EXP_OR = "The logical or operation takes a number boolean values and returns True if any of the values are True (False if all are not). " + SUB_EXP_BOP

EXP_EQ = "This operation compares two expressions to see if they have the same value. True is returned if the values are the same, and false if they are not. "
EXP_NEQ = "This operation compares two expressions to see if they do not have the same value. True is returned if the values are the different, and false if they are the same. "
EXP_LT = "This operation compares two expressions. It will return True if the value of left expression is smaller than the value of the right expression. "
EXP_LTE = "This operation compares two expressions. It will return True if the value of left expression is smaller than or equal to the value of the right expression. "
EXP_GT = "This operation compares two expressions. It will return True if the value of left expression is larger than the value of the right expression. "
EXP_GTE = "This operation compares two expressions. It will return True if the value of left expression is larger than or equal to the value of the right expression. "
EXP_IN = "This operation tells us if a particular value (left side) is contained in the sequence (or other data structure) named on the right side. The operation returns True if the value is found. "
EXP_NIN = "This operation tells us if a particular value (left side) is not contained in the sequence (or other data structure) named on the right side. The operation returns True if the value is not found. "

EXP_USUB = "The unary subtraction operation is a unary (only one part) operator that signifies that the value given should be changed from positive to negative (or negative to positive). "
EXP_UADD = "You really shouldn't be seeing this, there may be a problem in the code if this message appears in the question or feedback!"
EXP_NOT = "The unary logical not operation is a unary (only one part) operator that signifies that the boolean value given should be changed from True to False (or False to True). "
EXP_BNOT = "The unary binary not operation is a unary (only one part) operator that signifies that the individual bits in the number value given should be changed from 0 to 1 (or 1 to 0). "

# EXP_DECL = "This operation creates a new variable that can be used to remember a value. Generally, there are no more actions to complete in declaring a new variable. There are some exceptions, sometimes an assignment is carried out while a variable is being created. Additionally, if we are defining an array, we will need to calculate the size that the array is to be, this might be a constant or a variable we need to load the value of. "

EXP_LOAD_LIST = "This operation is similar to loading the value remembered from a variable, but in this case an index is used to identify which element of a list is returned. We will need to evaluate an expression to know what the value of the index we will load is before we can load the value stored in the list. "

EXP_LOAD_TARGET = "This operation is where we find the location of a variable in memory. This allows us to remember a new value in this location when using an assignment. "
SUB_EXP_LOAD_TARGET = "For a normal variable, there is no further work to be done, but if variable we are going to use is an array, we may need to calculate what index in the array the new value will be saved to. "

EXP_DEFINE_LIST = "This operation creates a list containing the value of the expressions that are separated by comas in the definition. Before we can create the list, we must evaluate the value of any of the expressions it contains. These will be evaluated from left to right. "

"""These are the C specific constants"""
M_DEC = "Variable Declaration"
M_ARR_DEC = "Array Variable Declaration"
M_VAR_INIT = "Variable Initialisation"
M_ARR_INIT = "Array Initialisation"
M_ARR_CONST = "Literal Array Definition"
M_DEREF = "Get Value from Address"
M_REF = "Get Address of Variable"
EXP_VAR_DECL = "The operation of variable declaration is where a new variable is created in the program. "
EXP_ARR_DECL = ""
EXP_REF = "This operation is called referencing and get the address of a variable that we are using. There are no other steps required to complete it."
EXP_DEREF = "This operation is called dereferencing and get a value from an address in memory. There are no other steps required to complete it."
EXP_ARR_CONST = "This operation defines the values of some elements to be put into an array. It can only be done when the array is first declared."
EXP_ARR_INIT = "The values defined in the literal array definition are stored in the relative position in the array, all remaining values are set to zero."
EXP_VAR_INIT = ""

top_ops = {M_ASS, M_FUN, M_IF, M_WHILE}
other_ops = {M_VAR, M_CONST, M_LOAD_LIST, M_DEF_LIST}
str_ops = {M_CON, M_REP}
bool_ops = {M_AND, M_OR}
comp_ops = {M_EQC, M_NEC, M_GTC, M_GTE, M_LTE, M_LTC}
math_ops = {M_ADD, M_SUB, M_MUL, M_DIV, M_IDIV, M_MOD, M_EXP}
operations = top_ops | str_ops | bool_ops | comp_ops | math_ops | other_ops

tags = {
    M_ASS: M_ASS,
    M_DEC: M_DEC,
    M_FUN: "Function",
    M_VAR: "Variable",
    M_LOAD_LIST: "Sequence",
    M_DEF_LIST: "List Def",
    M_CONST: "Constant",
    M_IF: "If",
    M_WHILE: "While",
    M_ADD: M_ADD,
    M_CON: M_CON,
    M_SUB: M_SUB,
    M_MUL: M_MUL,
    M_REP: M_REP,
    M_DIV: M_DIV,
    M_IDIV: "Int Division",
    M_MOD: M_MOD,
    M_EXP: M_EXP,
    M_UADD: "U Add",
    M_USUB: "U Sub",
    M_NOT: "Not",
    M_BNOT: "Bitflip",
    M_EQC: "Eq",
    M_NEC: "Neq",
    M_LTC: "Lt",
    M_LTE: "Lte",
    M_GTC: "Gt",
    M_GTE: "Gte",
    M_AND: "And",
    M_OR: "Or",
    M_REF: "Reference",
    M_ARR_DEC: "Array Declaration",
    M_VAR_INIT: "Variable Initialisation",
    M_ARR_INIT: M_ARR_INIT,
    M_ARR_CONST: M_ARR_CONST,
    M_LOAD_ARRAY: M_LOAD_ARRAY
}


def get_tag(explanation: str) -> str:
    return tags[explanation]


def get_wrong_answer(ans: str) -> Set[str]:
    return operations - set((ans,))


def get_wrong_answer_multi(ans: str) -> Set[str]:
    return {M_ASS, M_IF, M_FUN, M_WHILE, M_FIN} - set((ans,))

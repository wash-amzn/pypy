from rpython.jit.tl.threadedcode import tla

code = [
    tla.CONST_INT, 7,
    tla.DUP,
    tla.CALL_ASSEMBLER, 11, 1,
    tla.DUP,
    tla.PRINT,
    tla.POP1,
    tla.POP1,
    tla.EXIT,
    tla.DUPN, 1,
    tla.CONST_INT, 1,
    tla.LT,
    tla.JUMP_IF, 47,
    tla.DUPN, 1,
    tla.CONST_INT, 1,
    tla.SUB,
    tla.DUP,
    tla.CALL_ASSEMBLER, 11, 1,
    tla.DUPN, 3,
    tla.CONST_INT, 2,
    tla.SUB,
    tla.DUP,
    tla.CALL_ASSEMBLER, 11, 1,
    tla.DUPN, 2,
    tla.DUPN, 1,
    tla.ADD,
    tla.POP1,
    tla.POP1,
    tla.POP1,
    tla.POP1,
    tla.JUMP, 49,
    tla.CONST_INT, 1,
    tla.RET, 1,
]

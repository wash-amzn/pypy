from rpython.jit.tl.threadedcode import tla

code = [
    tla.CONST_N, 0, 1, 134, 160, 
    tla.CONST_INT, 100, 
    tla.CONST_INT, 42, 
    tla.CONST_INT, 2, 
    tla.DUP, 
    tla.DUPN, 2, 
    tla.BUILD_LIST, 
    tla.DUPN, 3, 
    tla.DUPN, 5, 
    tla.DUPN, 2, 
    tla.CALL_ASSEMBLER, 66, 3, 
    tla.DUP, 
    tla.PRINT, 
    tla.POP1, 
    tla.POP1, 
    tla.POP1, 
    tla.POP1, 
    tla.POP1, 
    tla.POP1, 
    tla.EXIT, 
    tla.DUPN, 1, 
    tla.CONST_INT, 1, 
    tla.SUB, 
    tla.DUP, 
    tla.DUPN, 4, 
    tla.LT, 
    tla.JUMP_IF, 48, 
    tla.DUPN, 3, 
    tla.JUMP, 63, 
    tla.DUPN, 3, 
    tla.DUPN, 3, 
    tla.SUB, 
    tla.DUP, 
    tla.DUPN, 4, 
    tla.FRAME_RESET, 2, 2, 2, 
    tla.JUMP, 33, 
    tla.POP1, 
    tla.POP1, 
    tla.RET, 2, 
    tla.CONST_N, 0, 0, 54, 174, 
    tla.DUPN, 3, 
    tla.CONST_INT, 2, 
    tla.GT, 
    tla.JUMP_IF, 82, 
    tla.CONST_INT, 0, 
    tla.JUMP, 150, 
    tla.DUPN, 2, 
    tla.CONST_INT, 0, 
    tla.LOAD, 
    tla.DUP, 
    tla.CONST_N, 0, 0, 15, 37, 
    tla.MUL, 
    tla.DUP, 
    tla.CONST_N, 0, 0, 115, 133, 
    tla.ADD, 
    tla.DUP, 
    tla.DUPN, 4, 
    tla.CALL_ASSEMBLER, 33, 2, 
    tla.DUPN, 8, 
    tla.DUPN, 1, 
    tla.MUL, 
    tla.DUP, 
    tla.CONST_N, 0, 0, 54, 174, 
    tla.DIV, 
    tla.DUP, 
    tla.DUPN, 9, 
    tla.CONST_INT, 0, 
    tla.STORE, 
    tla.DUPN, 10, 
    tla.CONST_INT, 1, 
    tla.SUB, 
    tla.DUPN, 12, 
    tla.DUPN, 1, 
    tla.DUPN, 12, 
    tla.FRAME_RESET, 3, 9, 3, 
    tla.JUMP, 66, 
    tla.POP1, 
    tla.POP1, 
    tla.POP1, 
    tla.POP1, 
    tla.POP1, 
    tla.POP1, 
    tla.POP1, 
    tla.POP1, 
    tla.POP1, 
    tla.RET, 3, 
]
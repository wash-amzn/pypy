from rpython.rtyper.lltypesystem import lltype, rffi
from pypy.interpreter.error import OperationError, oefmt
from pypy.module._hpy_universal.apiset import API
from pypy.module._hpy_universal import handles

@API.func("HPy HPyFloat_FromDouble(HPyContext ctx, double v)")
def HPyFloat_FromDouble(space, state, ctx, v):
    w_obj = space.newfloat(v)
    return state.handles.new(w_obj)

@API.func("double HPyFloat_AsDouble(HPyContext ctx, HPy h)", error_value=-1.0)
def HPyFloat_AsDouble(space, state, ctx, h):
    # XXX: the cpyext version calls space.float_w(space.float(w_obj)): we need
    # to add a test in HPy to test for that, and fix
    w_obj = state.handles.deref(h)
    value = space.float_w(w_obj)
    return value
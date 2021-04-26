from rpython.rtyper.lltypesystem import rffi, lltype
from pypy.interpreter.error import OperationError, oefmt
from pypy.objspace.std.listobject import W_ListObject
from pypy.module._hpy_universal.apiset import API
from pypy.module._hpy_universal import handles

@API.func("HPy HPyList_New(HPyContext ctx, HPy_ssize_t len)")
def HPyList_New(space, state, ctx, len):
    if len == 0:
        w_list = space.newlist([])
    else:
        w_list = space.newlist([None] * len)
    return state.handles.new(w_list)

@API.func("int HPyList_Check(HPyContext ctx, HPy h)", error_value='CANNOT_FAIL')
def HPyList_Check(space, state, ctx, h):
    w_obj = state.handles.deref(h)
    w_obj_type = space.type(w_obj)
    res = (space.is_w(w_obj_type, space.w_list) or
           space.issubtype_w(w_obj_type, space.w_list))
    return API.int(res)

@API.func("int HPyList_Append(HPyContext ctx, HPy h_list, HPy h_item)",
          error_value=API.int(-1))
def HPyList_Append(space, state, ctx, h_list, h_item):
    w_list = state.handles.deref(h_list)
    # XXX the tests should check what happens in this case
    assert isinstance(w_list, W_ListObject)
    w_item = state.handles.deref(h_item)
    w_list.append(w_item)
    return API.int(0)
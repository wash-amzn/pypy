import sys
from rpython.rlib.debug import check_nonneg
from rpython.rlib.rarithmetic import r_uint, intmask
from rpython.rlib.rsre.rsre_core import AbstractMatchContext, EndOfString
from rpython.rlib.rsre import rsre_char
from rpython.rlib.objectmodel import we_are_translated
from rpython.rlib import rutf8


class Utf8MatchContext(AbstractMatchContext):
    """A context that matches unicode, but encoded in a utf8 string.
    Be careful because most positions taken by, handled in, and returned
    by this class are expressed in *bytes*, not in characters.
    """

    def __init__(self, pattern, utf8string, match_start, end, flags):
        AbstractMatchContext.__init__(self, pattern, match_start, end, flags)
        self._utf8 = utf8string

    def str(self, index):
        check_nonneg(index)
        return rutf8.codepoint_at_pos(self._utf8, index)

    def lowstr(self, index):
        c = self.str(index)
        return rsre_char.getlower(c, self.flags)

    def get_single_byte(self, base_position, index):
        return self.str(base_position + index)

    def fresh_copy(self, start):
        return Utf8MatchContext(self.pattern, self._utf8, start,
                                self.end, self.flags)

    def next(self, position):
        return rutf8.next_codepoint_pos(self._utf8, position)

    def prev(self, position):
        if position <= 0:
            raise EndOfString
        upos = r_uint(position)
        upos = rutf8.prev_codepoint_pos(self._utf8, upos)
        position = intmask(upos)
        assert position >= 0
        return position

    def next_n(self, position, n, end_position):
        for i in range(n):
            if position >= end_position:
                raise EndOfString
            position = rutf8.next_codepoint_pos(self._utf8, position)
        return position

    def prev_n(self, position, n, start_position):
        upos = r_uint(position)
        for i in range(n):
            if upos <= r_uint(start_position):
                raise EndOfString
            upos = rutf8.next_codepoint_pos(self._utf8, upos)
        position = intmask(upos)
        assert position >= 0
        return position

    def debug_check_pos(self, position):
        if we_are_translated():
            return
        if position == len(self._utf8):
            return   # end of string is fine
        assert not (0x80 <= self._utf8[position] < 0xC0)   # continuation byte


def utf8search(pattern, utf8string, bytestart=0, byteend=sys.maxint, flags=0):
    # bytestart and byteend must be valid byte positions inside the
    # utf8string.
    from rpython.rlib.rsre.rsre_core import search_context

    assert 0 <= bytestart <= len(utf8string)
    assert 0 <= byteend
    if byteend > len(utf8string):
        byteend = len(utf8string)
    ctx = Utf8MatchContext(pattern, utf8string, bytestart, byteend, flags)
    ctx.debug_check_pos(bytestart)
    ctx.debug_check_pos(byteend)
    if search_context(ctx):
        return ctx
    else:
        return None

def utf8match(*args, **kwds):
    NOT_IMPLEMENTED

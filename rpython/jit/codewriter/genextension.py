import py
from rpython.jit.metainterp.history import (Const, ConstInt, ConstPtr,
    ConstFloat, CONST_NULL)

class GenExtension(object):
    def __init__(self, assembler):
        self.assembler = assembler
        self.insns = [None] * len(assembler.insns)
        for insn, index in assembler.insns.iteritems():
            self.insns[index] = insn

    def setup(self, ssarepr, jitcode):
        self.ssarepr = ssarepr
        self.jitcode = jitcode
        self.precode = []
        self.code = []
        self.globals = {}

    def generate(self, ssarepr, jitcode):
        from rpython.jit.codewriter.flatten import Label
        from rpython.jit.codewriter.jitcode import JitCode
        self.setup(ssarepr, jitcode)
        self.precode.append("def jit_shortcut(self):")
        self.precode.append("    pc = self.pc")
        self.precode.append("    while 1:")
        for index, insn in enumerate(ssarepr.insns):
            if isinstance(insn[0], Label) or insn[0] == '---':
                continue
            pc = ssarepr._insns_pos[index]
            self.code.append("if pc == %s:" % pc)
            if index == len(self.ssarepr.insns) - 1:
                nextpc = len(self.jitcode.code)
            else:
                nextpc = self.ssarepr._insns_pos[index + 1]
            lines, needed_orgpc, needed_label = self._emit_instruction(insn, index, pc, nextpc)
            for line in lines:
                self.code.append("    " + line)
            pcs = self.next_possible_pcs(insn, needed_label, nextpc)
            if len(pcs) == 0:
                self.code.append("    assert 0 # unreachable")
                continue
            elif len(pcs) == 1:
                self.code.append("    pc = %s" % pcs[0])
            else:
                self.code.append("    pc = self.pc")
                # do the trick
                prefix = ''
                for pc in pcs:
                    self.code.append("    %sif pc == %s: pc = %s" % (prefix, pc, pc))
                    prefix = "el"
                self.code.append("    else:")
                self.code.append("        assert 0 # unreachable")
            self.code.append("    continue")
        self.code.append("assert 0 # unreachable")
        allcode = []
        allcode.extend(self.precode)
        for line in self.code:
            allcode.append(" " * 8 + line)
        jitcode._genext_source = "\n".join(allcode)
        d = {"ConstInt": ConstInt, "JitCode": JitCode}
        source = py.code.Source(jitcode._genext_source)
        exec source.compile() in d
        print jitcode._genext_source
        jitcode.genext_function = d['jit_shortcut']

    def _emit_instruction(self, insn, index, pc, nextpc):
        from rpython.jit.metainterp.pyjitpl import MIFrame
        from rpython.jit.metainterp.blackhole import signedord
        lines = []
        # first, write self.pc
        lines.append("self.pc = %s" % (nextpc, ))
        if insn[0] == '-live-':
            lines.append('pass # live')
            return lines, False, None

        instruction = self.insns[ord(self.jitcode.code[pc])]
        name, argcodes = instruction.split("/")
        methodname = 'opimpl_' + name
        unboundmethod = getattr(MIFrame, methodname).im_func
        argtypes = unboundmethod.argtypes

        # collect arguments, this is a 'timeshifted' version of the code in
        # pyjitpl._get_opimpl_method
        args = []
        next_argcode = 0
        code = self.jitcode.code
        orgpc = pc
        position = pc
        position += 1
        needed_orgpc = False
        needed_label = None
        for argtype in argtypes:
            if argtype == "box":     # a box, of whatever type
                argcode = argcodes[next_argcode]
                next_argcode = next_argcode + 1
                if argcode == 'i':
                    value = "self.registers_i[%s]" % (ord(code[position]), )
                elif argcode == 'c':
                    value = "ConstInt(%s)" % signedord(code[position])
                elif argcode == 'r':
                    value = "self.registers_r[%s]" % (ord(code[position]), )
                elif argcode == 'f':
                    value = "self.registers_f[%s]" % (ord(code[position]), )
                else:
                    raise AssertionError("bad argcode")
                position += 1
            elif argtype == "descr" or argtype == "jitcode":
                assert argcodes[next_argcode] == 'd'
                next_argcode = next_argcode + 1
                index = ord(code[position]) | (ord(code[position+1])<<8)
                argname = "arg%s" % position
                self.code.append("    %s = self.metainterp.staticdata.opcode_descrs[%s]" % (argname, index))
                value = argname
                if argtype == "jitcode":
                    self.code.append("    assert isinstance(%s, JitCode)" % argname)
                position += 2
            elif argtype == "label":
                assert argcodes[next_argcode] == 'L'
                next_argcode = next_argcode + 1
                assert needed_label is None # only one label per instruction
                needed_label = ord(code[position]) | (ord(code[position+1])<<8)
                value = str(needed_label)
                position += 2
            elif argtype == "boxes":     # a list of boxes of some type
                length = ord(code[position])
                value = [None] * length
                self.prepare_list_of_boxes(value, 0, position,
                                           argcodes[next_argcode])
                next_argcode = next_argcode + 1
                position += 1 + length
                value = '[' + ",".join(value) + "]"
            elif argtype == "boxes2":     # two lists of boxes merged into one
                length1 = ord(code[position])
                position2 = position + 1 + length1
                length2 = ord(code[position2])
                value = [None] * (length1 + length2)
                self.prepare_list_of_boxes(value, 0, position,
                                           argcodes[next_argcode])
                self.prepare_list_of_boxes(value, length1, position2,
                                           argcodes[next_argcode + 1])
                next_argcode = next_argcode + 2
                position = position2 + 1 + length2
                value = '[' + ",".join(value) + "]"
            elif argtype == "boxes3":    # three lists of boxes merged into one
                length1 = ord(code[position])
                position2 = position + 1 + length1
                length2 = ord(code[position2])
                position3 = position2 + 1 + length2
                length3 = ord(code[position3])
                value = [None] * (length1 + length2 + length3)
                self.prepare_list_of_boxes(value, 0, position,
                                           argcodes[next_argcode])
                self.prepare_list_of_boxes(value, length1, position2,
                                           argcodes[next_argcode + 1])
                self.prepare_list_of_boxes(value, length1 + length2, position3,
                                           argcodes[next_argcode + 2])
                next_argcode = next_argcode + 3
                position = position3 + 1 + length3
                value = '[' + ",".join(value) + "]"
            elif argtype == "newframe" or argtype == "newframe2" or argtype == "newframe3":
                assert argtypes == (argtype, )
                # this and the next two are basically equivalent to
                # jitcode boxes/boxes2/boxes3
                # instead of allocating the list of boxes, just put everything
                # into the correct position of a new MIFrame

                # first get the jitcode
                assert argcodes[next_argcode] == 'd'
                next_argcode = next_argcode + 1
                index = ord(code[position]) | (ord(code[position+1])<<8)
                value = argname = "arg%s" % position
                lines.append("jitcode = self.metainterp.staticdata.opcode_descrs[%s]" % (index, ))
                lines.append("assert isinstance(jitcode, JitCode)")
                position += 2
                # make a new frame
                lines.append("%s = self.metainterp.newframe(jitcode)" % (argname, ))
                lines.append("%s.pc = 0" % (argname, ))

                # generate code to put boxes into the right places
                length = ord(code[position])
                self.fill_registers(lines, argname, length, position + 1,
                                    argcodes[next_argcode])
                next_argcode = next_argcode + 1
                position += 1 + length
                if argtype != "newframe": # 2/3 lists of boxes
                    length = ord(code[position])
                    self.fill_registers(lines, argname, length, position + 1,
                                        argcodes[next_argcode])
                    next_argcode = next_argcode + 1
                    position += 1 + length
                if argtype == "newframe3": # 3 lists of boxes
                    length = ord(code[position])
                    self.fill_registers(lines, argname, length, position + 1,
                                        argcodes[next_argcode])
                    next_argcode = next_argcode + 1
                    position += 1 + length
                lines.append("return # change frame %s" % (insn, ))
                return lines, needed_orgpc, needed_label
            elif argtype == "orgpc":
                value = str(orgpc)
                needed_orgpc = True
            elif argtype == "int":
                argcode = argcodes[next_argcode]
                next_argcode = next_argcode + 1
                if argcode == 'i':
                    pos = ord(code[position])
                    if 255 - pos < len(self.jitcode.constants_i):
                        value = str(self.jitcode.constants_i[255 - pos])
                    else:
                        value = "self.registers_i[%s].getint()" % (pos, )
                elif argcode == 'c':
                    value = str(signedord(code[position]))
                else:
                    raise AssertionError("bad argcode")
                position += 1
            elif argtype == "jitcode_position":
                value = str(position)
            else:
                raise AssertionError("bad argtype: %r" % (argtype,))
            args.append(value)
        strargs = ", ".join(args)

        if insn[0] == "goto":
            assert len(args) == 1
            lines.append("pc = self.pc = %s # goto" % (args[0], ))
            lines.append("continue")
            return lines, needed_orgpc, needed_label

        num_return_args = len(argcodes) - next_argcode
        assert num_return_args == 0 or num_return_args == 2
        if num_return_args:
            # Save the type of the resulting box.  This is needed if there is
            # a get_list_of_active_boxes().  See comments there.
            lines.append("self._result_argcode = %r" % (argcodes[next_argcode + 1], ))
            resindex = ord(code[position])
            if argcodes[next_argcode + 1] == "i":
                prefix = "self.registers_i[%s] = " % resindex
            elif argcodes[next_argcode + 1] == "r":
                prefix = "self.registers_r[%s] = " % resindex
            elif argcodes[next_argcode + 1] == "f":
                prefix = "self.registers_f[%s] = " % resindex
            else:
                assert 0
            position += 1
        else:
            lines.append("self._result_argcode = 'v'")
            prefix = ''

        lines.append("%sself.%s(%s)" % (prefix, methodname, strargs))
        return lines, needed_orgpc, needed_label

    def prepare_list_of_boxes(self, outvalue, startindex, position, argcode):
        assert argcode in 'IRF'
        code = self.jitcode.code
        length = ord(code[position])
        position += 1
        for i in range(length):
            index = ord(code[position+i])
            if   argcode == 'I': reg = "self.registers_i[%s]" % index
            elif argcode == 'R': reg = "self.registers_r[%s]" % index
            elif argcode == 'F': reg = "self.registers_f[%s]" % index
            else: raise AssertionError(argcode)
            outvalue[startindex+i] = reg

    def fill_registers(self, lines, argname, length, position, argcode):
        assert argcode in 'IRF'
        code = self.jitcode.code
        for i in range(length):
            index = ord(code[position+i])
            if   argcode == 'I':
                lines.append("%s.registers_i[%s] = self.registers_i[%s]" % (argname, i, index))
            elif argcode == 'R':
                lines.append("%s.registers_r[%s] = self.registers_r[%s]" % (argname, i, index))
            elif argcode == 'F':
                lines.append("%s.registers_f[%s] = self.registers_f[%s]" % (argname, i, index))
            else:
                raise AssertionError(argcode)

    def next_possible_pcs(self, insn, needed_label, nextpc):
        if insn[0] == "goto":
            return [needed_label]
        if needed_label is not None:
            return [nextpc, needed_label]
        if insn[0].endswith("return"):
            return []
        if insn[0].endswith("raise"):
            return []
        if insn[0] == "switch":
            return insn[2].dict.values() + [nextpc]
        else:
            return [nextpc]


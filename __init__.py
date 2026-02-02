import enum
from typing import Optional, Tuple, List

from binaryninja import Architecture, RegisterInfo, InstructionInfo, InstructionTextToken, \
    InstructionTextTokenType, BinaryViewType, Endianness, BranchType



class QuarkInstruction:
    def __init__(self, instr: int):
        self.instr = instr

    @property
    def cond(self):
        return self.instr >> 28

    @property
    def op(self):
        return (self.instr >> 22) & 0x3f

    @property
    def a(self):
        return (self.instr >> 17) & 31

    @property
    def b(self):
        return (self.instr >> 12) & 31

    @property
    def c(self):
        return (self.instr >> 5) & 31

    @property
    def d(self):
        return self.instr & 31

    @property
    def imm5i(self):
        if self.instr & 0x10:
            return -(self.instr & 0x1f)
        return self.instr & 0x1f

    @property
    def imm5(self):
        if self.instr & 0x10:
            return (self.instr & 0x1f) | 0xffffffe0
        return self.instr & 0x1f

    @property
    def imm11i(self):
        if self.instr & 0x400:
            return -(self.instr & 0x7ff)
        return self.instr & 0x7ff

    @property
    def imm11(self):
        if self.instr & 0x400:
            return (self.instr & 0x7ff) | 0xfffff800
        return self.instr & 0x7ff

    @property
    def imm17i(self):
        if self.instr & 0x10000:
            return -(self.instr & 0x1ffff)
        return self.instr & 0x1ffff

    @property
    def imm17(self):
        if self.instr & 0x10000:
            return (self.instr & 0x1ffff) | 0xfffe0000
        return self.instr & 0x1ffff

    @property
    def imm22i(self):
        if self.instr & 0x200000:
            return -(self.instr & 0x3fffff)
        return self.instr & 0x3fffff

    @property
    def imm22(self):
        if self.instr & 0x200000:
            return (self.instr & 0x3fffff) | 0xffc00000
        return self.instr & 0x3fffff

    @property
    def immhi(self):
        return (self.instr & 0xffff) << 16

    @property
    def smallimm(self):
        return self.instr & 0x400

    @property
    def largeimm(self):
        return self.instr & 0x800


class QuarkArch(Architecture):
    name = "Quark"
    address_size = 4
    default_int_size = 4
    instr_alignment = 1
    max_instr_length = 4
    regs = {
        'sp': RegisterInfo('sp', 4),
        'r1': RegisterInfo('r1', 4),
        'r2': RegisterInfo('r2', 4),
        'r3': RegisterInfo('r3', 4),
        'r4': RegisterInfo('r4', 4),
        'r5': RegisterInfo('r5', 4),
        'r6': RegisterInfo('r6', 4),
        'r7': RegisterInfo('r7', 4),
        'r8': RegisterInfo('r8', 4),
        'r9': RegisterInfo('r9', 4),
        'r10': RegisterInfo('r10', 4),
        'r11': RegisterInfo('r11', 4),
        'r12': RegisterInfo('r12', 4),
        'r13': RegisterInfo('r13', 4),
        'r14': RegisterInfo('r14', 4),
        'r15': RegisterInfo('r15', 4),
        'r16': RegisterInfo('r16', 4),
        'r17': RegisterInfo('r17', 4),
        'r18': RegisterInfo('r18', 4),
        'r19': RegisterInfo('r19', 4),
        'r20': RegisterInfo('r20', 4),
        'r21': RegisterInfo('r21', 4),
        'r22': RegisterInfo('r22', 4),
        'r23': RegisterInfo('r23', 4),
        'r24': RegisterInfo('r24', 4),
        'r25': RegisterInfo('r25', 4),
        'r26': RegisterInfo('r26', 4),
        'r27': RegisterInfo('r27', 4),
        'r28': RegisterInfo('r28', 4),
        'r29': RegisterInfo('r29', 4),
        'lr': RegisterInfo('lr', 4),
        'ip': RegisterInfo('ip', 4),
        'cc0': RegisterInfo('cc0', 1),
        'cc1': RegisterInfo('cc1', 1),
        'cc2': RegisterInfo('cc2', 1),
        'cc3': RegisterInfo('cc3', 1),
    }
    stack_pointer = 'sp'
    link_reg = 'lr'

    def get_instruction_info(self, data: bytes, addr: int) -> Optional[InstructionInfo]:
        result = InstructionInfo()
        result.length = 4
        return result

    def get_instruction_text(self, data: bytes, addr: int) -> Optional[Tuple[List['function.InstructionTextToken'], int]]:
        info = QuarkInstruction(int.from_bytes(data, 'little'))

        tokens = []
        tokens.extend([
            InstructionTextToken(InstructionTextTokenType.TextToken, 'cond: '),
            InstructionTextToken(InstructionTextTokenType.TextToken, f'{info.cond}'),
            InstructionTextToken(InstructionTextTokenType.TextToken, ' op: '),
            InstructionTextToken(InstructionTextTokenType.TextToken, f'{info.op}'),
            InstructionTextToken(InstructionTextTokenType.TextToken, ' a: '),
            InstructionTextToken(InstructionTextTokenType.TextToken, f'{info.a}'),
            InstructionTextToken(InstructionTextTokenType.TextToken, ' b: '),
            InstructionTextToken(InstructionTextTokenType.TextToken, f'{info.b}'),
            InstructionTextToken(InstructionTextTokenType.TextToken, ' c: '),
            InstructionTextToken(InstructionTextTokenType.TextToken, f'{info.c}'),
            InstructionTextToken(InstructionTextTokenType.TextToken, ' d: '),
            InstructionTextToken(InstructionTextTokenType.TextToken, f'{info.d}'),
        ])

        return tokens, 4


QuarkArch.register()
BinaryViewType['ELF'].register_arch(4242, Endianness.LittleEndian, Architecture['Quark'])


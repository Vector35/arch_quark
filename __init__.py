import enum
from typing import Optional, Tuple, List

from binaryninja import Architecture, RegisterInfo, InstructionInfo, InstructionTextToken, \
    InstructionTextTokenType, BinaryViewType, Endianness, BranchType, lowlevelil, \
    LowLevelILLabel, LowLevelILFunction, LLIL_TEMP, FlagRole, LowLevelILOperation, \
    FlagWriteTypeName, FlagType, ILRegisterType, ExpressionIndex, IntrinsicInfo, Type, \
    IntrinsicInput, CallingConvention, Platform


def rol(i, n):
    return ((i << n) & 0xffffffff) | (i >> (32 - n))


def ror(i, n):
    return (i >> n) | ((i << (32 - n)) & 0xffffffff)


def i32(i):
    if i >= 0x80000000:
        return -(0x100000000 - (i & 0xffffffff))
    return i & 0x7fffffff


class QuarkOpcode(enum.IntEnum):
    ldb = 0x0
    ldh = 0x1
    ldw = 0x2
    ldmw = 0x3
    stb = 0x4
    sth = 0x5
    stw = 0x6
    stmw = 0x7
    ldbu = 0x8
    ldhu = 0x9
    ldwu = 0xa
    ldmwu = 0xb
    stbu = 0xc
    sthu = 0xd
    stwu = 0xe
    stmwu = 0xf
    ldsxb = 0x10
    ldsxh = 0x11
    ldsxbu = 0x12
    ldsxhu = 0x13
    ldi = 0x14
    ldih = 0x15
    jmp = 0x16
    call = 0x17
    add = 0x18
    sub = 0x19
    addx = 0x1a
    subx = 0x1b
    mulx = 0x1c
    imulx = 0x1d
    mul = 0x1e
    integer_group = 0x1f
    div = 0x20
    idiv = 0x21
    mod = 0x22
    imod = 0x23
    and_ = 0x24
    or_ = 0x25
    xor = 0x26
    sar = 0x27
    shl = 0x28
    shr = 0x29
    rol = 0x2a
    ror = 0x2b
    syscall = 0x2c
    cmp = 0x2d
    icmp = 0x2e


class QuarkIntegerOpcode(enum.IntEnum):
    mov = 0x0
    xchg = 0x1
    sxb = 0x2
    sxh = 0x3
    swaph = 0x4
    swapw = 0x5
    call = 0x6
    neg = 0x8
    not_ = 0x9
    zxb = 0xa
    zxh = 0xb
    ldcr = 0xe
    stcr = 0xf
    syscall = 0x10
    setcc = 0x18
    clrcc = 0x19
    notcc = 0x1a
    movcc = 0x1b
    andcc = 0x1c
    orcc = 0x1d
    xorcc = 0x1e


class QuarkCompareOpcode(enum.IntEnum):
    lt = 0
    le = 1
    ge = 2
    gt = 3
    eq = 4
    ne = 5
    nz = 6
    z = 7


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
    def imm5(self):
        if self.instr & 0x10:
            return (self.instr & 0x1f) | 0xffffffe0
        return self.instr & 0x1f

    @property
    def imm11(self):
        if self.instr & 0x400:
            return (self.instr & 0x7ff) | 0xfffff800
        return self.instr & 0x7ff

    @property
    def imm17(self):
        if self.instr & 0x10000:
            return (self.instr & 0x1ffff) | 0xfffe0000
        return self.instr & 0x1ffff

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
        'syscall_num': RegisterInfo('syscall_num', 4),
    }
    flags = {
        'cc0', 'cc1', 'cc2', 'cc3',
    }
    flag_roles = {
        'cc0': FlagRole.SpecialFlagRole,
        'cc1': FlagRole.SpecialFlagRole,
        'cc2': FlagRole.SpecialFlagRole,
        'cc3': FlagRole.SpecialFlagRole,
    }
    flag_write_types = {
        'none', '*', '0', '1', '2', '3'
    }
    flags_written_by_flag_write_type = {
        'none': {},
        '*': ['cc0', 'cc1', 'cc2', 'cc3'],
        '0': ['cc0'],
        '1': ['cc1'],
        '2': ['cc2'],
        '3': ['cc3'],
    }
    stack_pointer = 'sp'
    link_reg = 'lr'
    intrinsics = {
        '__byteswaph': IntrinsicInfo([IntrinsicInput(Type.int(2), '')], [Type.int(2, False)]),
        '__byteswapw': IntrinsicInfo([IntrinsicInput(Type.int(4), '')], [Type.int(4, False)]),
    }

    ip_reg_index = 31

    def get_instruction_info(self, data: bytes, addr: int) -> Optional[InstructionInfo]:
        info = QuarkInstruction(int.from_bytes(data, 'little'))
        try:
            op = QuarkOpcode(info.op)
        except ValueError:
            print(f"Invalid opcode {info.op:#x} at {addr:#x} {data}")
            return None

        result = InstructionInfo()
        result.length = 4

        match op:
            case QuarkOpcode.jmp:
                if info.cond & 8:
                    if info.cond & 1:
                        result.add_branch(BranchType.TrueBranch, addr + 4 + i32(info.imm22 << 2))
                        result.add_branch(BranchType.FalseBranch, addr + 4)
                    else:
                        result.add_branch(BranchType.TrueBranch, addr + 4)
                        result.add_branch(BranchType.FalseBranch, addr + 4 + i32(info.imm22 << 2))
                else:
                    result.add_branch(BranchType.UnconditionalBranch, addr + 4 + i32(info.imm22 << 2))
            case QuarkOpcode.call:
                result.add_branch(BranchType.CallDestination, addr + 4 + i32(info.imm22 << 2))
            case QuarkOpcode.syscall:
                result.add_branch(BranchType.SystemCall)
            case QuarkOpcode.integer_group:
                int_op = QuarkIntegerOpcode(info.b)
                match int_op:
                    case QuarkIntegerOpcode.mov:
                        if info.a == self.ip_reg_index:
                            result.add_branch(BranchType.IndirectBranch)
                    case QuarkIntegerOpcode.call:
                        result.add_branch(BranchType.CallDestination)
                    case QuarkIntegerOpcode.syscall:
                        result.add_branch(BranchType.SystemCall)

        return result

    def get_instruction_text(self, data: bytes, addr: int) -> Optional[Tuple[List['function.InstructionTextToken'], int]]:
        info = QuarkInstruction(int.from_bytes(data, 'little'))
        try:
            op = QuarkOpcode(info.op)
        except ValueError:
            print(f"Invalid opcode {info.op:#x} at {addr:#x} {data}")
            return None

        tokens = []

        if info.cond & 8:
            if info.cond & 1:
                tokens.extend([
                    InstructionTextToken(InstructionTextTokenType.TextToken, "if"),
                    InstructionTextToken(InstructionTextTokenType.TextToken, " "),
                    InstructionTextToken(InstructionTextTokenType.RegisterToken, f"cc{(info.cond >> 1) & 3}"),
                    InstructionTextToken(InstructionTextTokenType.TextToken, " "),
                ])
            else:
                tokens.extend([
                    InstructionTextToken(InstructionTextTokenType.TextToken, "if"),
                    InstructionTextToken(InstructionTextTokenType.TextToken, " "),
                    InstructionTextToken(InstructionTextTokenType.OperationToken, "!"),
                    InstructionTextToken(InstructionTextTokenType.RegisterToken, f"cc{(info.cond >> 1) & 3}"),
                    InstructionTextToken(InstructionTextTokenType.TextToken, " "),
                ])
        elif info.cond & 1:
            tokens.extend([
                InstructionTextToken(InstructionTextTokenType.TextToken, "skip"),
                InstructionTextToken(InstructionTextTokenType.TextToken, " "),
            ])

        def reg_name(reg):
            if reg == self.ip_reg_index:
                return "ip"
            return self.get_reg_name(reg)

        def cval_tokens(plus: bool, zero: bool, signed: bool):
            if info.largeimm:
                if info.imm11 == 0:
                    if not zero:
                        return []
                    else:
                        if plus:
                            return [
                                InstructionTextToken(InstructionTextTokenType.OperationToken, f"+"),
                                InstructionTextToken(InstructionTextTokenType.IntegerToken, "0", value=0),
                            ]
                        else:
                            return [
                                InstructionTextToken(InstructionTextTokenType.IntegerToken, "0", value=0),
                            ]
                elif i32(info.imm11) > 0 or not signed:
                    if plus:
                        return [
                            InstructionTextToken(InstructionTextTokenType.OperationToken, f"+"),
                            InstructionTextToken(InstructionTextTokenType.IntegerToken, f"{info.imm11:#x}", value=info.imm11),
                        ]
                    else:
                        return [
                            InstructionTextToken(InstructionTextTokenType.IntegerToken, f"{info.imm11:#x}", value=info.imm11),
                        ]
                else:
                    if plus:
                        return [
                            InstructionTextToken(InstructionTextTokenType.OperationToken, f"-"),
                            InstructionTextToken(InstructionTextTokenType.IntegerToken, f"{-i32(info.imm11):#x}", value=i32(info.imm11)),
                        ]
                    else:
                        return [
                            InstructionTextToken(InstructionTextTokenType.IntegerToken, f"{i32(info.imm11):#x}", value=i32(info.imm11)),
                        ]
            elif info.smallimm:
                cval = rol(info.imm5, info.d)
                if cval == 0:
                    if not zero:
                        return []
                    else:
                        if plus:
                            return [
                                InstructionTextToken(InstructionTextTokenType.OperationToken, f"+"),
                                InstructionTextToken(InstructionTextTokenType.IntegerToken, "0", value=0),
                            ]
                        else:
                            return [
                                InstructionTextToken(InstructionTextTokenType.IntegerToken, "0", value=0),
                            ]
                elif cval > 0 or not signed:
                    if plus:
                        return [
                            InstructionTextToken(InstructionTextTokenType.OperationToken, f"+"),
                            InstructionTextToken(InstructionTextTokenType.IntegerToken, f"{cval:#x}", value=cval),
                        ]
                    else:
                        return [
                            InstructionTextToken(InstructionTextTokenType.IntegerToken, f"{cval:#x}", value=cval),
                        ]
                else:
                    if plus:
                        return [
                            InstructionTextToken(InstructionTextTokenType.OperationToken, f"-"),
                            InstructionTextToken(InstructionTextTokenType.IntegerToken, f"{i32(cval):#x}", value=-i32(cval)),
                        ]
                    else:
                        return [
                            InstructionTextToken(InstructionTextTokenType.IntegerToken, f"{cval:#x}", value=cval),
                        ]
            else:
                if info.d == 0:
                    if plus:
                        return [
                            InstructionTextToken(InstructionTextTokenType.OperationToken, f"+"),
                            InstructionTextToken(InstructionTextTokenType.RegisterToken, reg_name(info.c)),
                        ]
                    else:
                        return [
                            InstructionTextToken(InstructionTextTokenType.RegisterToken, reg_name(info.c)),
                        ]
                else:
                    if plus:
                        return [
                            InstructionTextToken(InstructionTextTokenType.OperationToken, f"+"),
                            InstructionTextToken(InstructionTextTokenType.RegisterToken, reg_name(info.c)),
                            InstructionTextToken(InstructionTextTokenType.OperationToken, f"*"),
                            InstructionTextToken(InstructionTextTokenType.IntegerToken, f"{2**info.d}", value=2**info.d),
                        ]
                    else:
                        return [
                            InstructionTextToken(InstructionTextTokenType.RegisterToken, reg_name(info.c)),
                            InstructionTextToken(InstructionTextTokenType.OperationToken, f"*"),
                            InstructionTextToken(InstructionTextTokenType.IntegerToken, f"{2**info.d}", value=2**info.d),
                        ]

        match op:
            case QuarkOpcode.ldb | QuarkOpcode.ldh | QuarkOpcode.ldw | QuarkOpcode.ldbu | QuarkOpcode.ldhu | QuarkOpcode.ldwu | QuarkOpcode.ldsxb | QuarkOpcode.ldsxh | QuarkOpcode.ldsxbu | QuarkOpcode.ldsxhu:
                tokens.extend([
                    InstructionTextToken(InstructionTextTokenType.InstructionToken, op.name),
                    InstructionTextToken(InstructionTextTokenType.TextToken, " "),
                    InstructionTextToken(InstructionTextTokenType.RegisterToken, reg_name(info.a)),
                    InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ", "),
                    InstructionTextToken(InstructionTextTokenType.BraceToken, "["),
                    InstructionTextToken(InstructionTextTokenType.RegisterToken, reg_name(info.b)),
                    *cval_tokens(plus=True, zero=False, signed=True),
                    InstructionTextToken(InstructionTextTokenType.BraceToken, "]"),
                ])
            case QuarkOpcode.ldmw | QuarkOpcode.ldmwu:
                tokens.extend([
                    InstructionTextToken(InstructionTextTokenType.InstructionToken, op.name),
                    InstructionTextToken(InstructionTextTokenType.TextToken, " "),
                    InstructionTextToken(InstructionTextTokenType.RegisterToken, reg_name(info.a)),
                    InstructionTextToken(InstructionTextTokenType.TextToken, ".."),
                    InstructionTextToken(InstructionTextTokenType.RegisterToken, reg_name(30)),
                    InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ", "),
                    InstructionTextToken(InstructionTextTokenType.BraceToken, "["),
                    InstructionTextToken(InstructionTextTokenType.RegisterToken, reg_name(info.b)),
                    InstructionTextToken(InstructionTextTokenType.BraceToken, "]"),
                ])
            case QuarkOpcode.ldi:
                tokens.extend([
                    InstructionTextToken(InstructionTextTokenType.InstructionToken, op.name),
                    InstructionTextToken(InstructionTextTokenType.TextToken, " "),
                    InstructionTextToken(InstructionTextTokenType.RegisterToken, reg_name(info.a)),
                    InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ", "),
                    InstructionTextToken(InstructionTextTokenType.IntegerToken, f"{info.imm17:#x}", value=info.imm17),
                ])
            case QuarkOpcode.ldih:
                tokens.extend([
                    InstructionTextToken(InstructionTextTokenType.InstructionToken, op.name),
                    InstructionTextToken(InstructionTextTokenType.TextToken, " "),
                    InstructionTextToken(InstructionTextTokenType.RegisterToken, reg_name(info.a)),
                    InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ", "),
                    InstructionTextToken(InstructionTextTokenType.IntegerToken, f"{info.immhi:#x}", value=info.immhi),
                ])
            case QuarkOpcode.stb | QuarkOpcode.sth | QuarkOpcode.stw | QuarkOpcode.stbu | QuarkOpcode.sthu | QuarkOpcode.stwu:
                tokens.extend([
                    InstructionTextToken(InstructionTextTokenType.InstructionToken, op.name),
                    InstructionTextToken(InstructionTextTokenType.TextToken, " "),
                    InstructionTextToken(InstructionTextTokenType.BraceToken, "["),
                    InstructionTextToken(InstructionTextTokenType.RegisterToken, reg_name(info.b)),
                    *cval_tokens(plus=True, zero=False, signed=True),
                    InstructionTextToken(InstructionTextTokenType.BraceToken, "]"),
                    InstructionTextToken(InstructionTextTokenType.TextToken, ", "),
                    InstructionTextToken(InstructionTextTokenType.RegisterToken, reg_name(info.a)),
                ])
            case QuarkOpcode.stmw | QuarkOpcode.stmwu:
                tokens.extend([
                    InstructionTextToken(InstructionTextTokenType.InstructionToken, op.name),
                    InstructionTextToken(InstructionTextTokenType.TextToken, " "),
                    InstructionTextToken(InstructionTextTokenType.BraceToken, "["),
                    InstructionTextToken(InstructionTextTokenType.RegisterToken, reg_name(info.b)),
                    InstructionTextToken(InstructionTextTokenType.BraceToken, "]"),
                    InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ", "),
                    InstructionTextToken(InstructionTextTokenType.RegisterToken, reg_name(info.a)),
                    InstructionTextToken(InstructionTextTokenType.TextToken, ".."),
                    InstructionTextToken(InstructionTextTokenType.RegisterToken, reg_name(30)),
                ])
            case QuarkOpcode.jmp | QuarkOpcode.call:
                dest = addr + 4 + i32(info.imm22 << 2)
                tokens.extend([
                    InstructionTextToken(InstructionTextTokenType.InstructionToken, op.name),
                    InstructionTextToken(InstructionTextTokenType.TextToken, " "),
                    InstructionTextToken(InstructionTextTokenType.PossibleAddressToken, f"{dest:#x}", value=dest),
                ])
            case QuarkOpcode.add | QuarkOpcode.sub | QuarkOpcode.mul | QuarkOpcode.div | QuarkOpcode.idiv | QuarkOpcode.mod | QuarkOpcode.imod:
                tokens.extend([
                    InstructionTextToken(InstructionTextTokenType.InstructionToken, op.name),
                    InstructionTextToken(InstructionTextTokenType.TextToken, " "),
                    InstructionTextToken(InstructionTextTokenType.RegisterToken, reg_name(info.a)),
                    InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ", "),
                    InstructionTextToken(InstructionTextTokenType.RegisterToken, reg_name(info.b)),
                    InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ", "),
                    *cval_tokens(plus=False, zero=True, signed=True),
                ])
            case QuarkOpcode.xor | QuarkOpcode.sar | QuarkOpcode.shl | QuarkOpcode.shr | QuarkOpcode.rol | QuarkOpcode.ror:
                tokens.extend([
                    InstructionTextToken(InstructionTextTokenType.InstructionToken, op.name),
                    InstructionTextToken(InstructionTextTokenType.TextToken, " "),
                    InstructionTextToken(InstructionTextTokenType.RegisterToken, reg_name(info.a)),
                    InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ", "),
                    InstructionTextToken(InstructionTextTokenType.RegisterToken, reg_name(info.b)),
                    InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ", "),
                    *cval_tokens(plus=False, zero=True, signed=False),
                ])
            case QuarkOpcode.and_:
                tokens.extend([
                    InstructionTextToken(InstructionTextTokenType.InstructionToken, "and"),
                    InstructionTextToken(InstructionTextTokenType.TextToken, " "),
                    InstructionTextToken(InstructionTextTokenType.RegisterToken, reg_name(info.a)),
                    InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ", "),
                    InstructionTextToken(InstructionTextTokenType.RegisterToken, reg_name(info.b)),
                    InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ", "),
                    *cval_tokens(plus=False, zero=True, signed=False),
                ])
            case QuarkOpcode.or_:
                tokens.extend([
                    InstructionTextToken(InstructionTextTokenType.InstructionToken, "or"),
                    InstructionTextToken(InstructionTextTokenType.TextToken, " "),
                    InstructionTextToken(InstructionTextTokenType.RegisterToken, reg_name(info.a)),
                    InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ", "),
                    InstructionTextToken(InstructionTextTokenType.RegisterToken, reg_name(info.b)),
                    InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ", "),
                    *cval_tokens(plus=False, zero=True, signed=False),
                ])
            case QuarkOpcode.addx | QuarkOpcode.subx:
                tokens.extend([
                    InstructionTextToken(InstructionTextTokenType.InstructionToken, op.name),
                    InstructionTextToken(InstructionTextTokenType.TextToken, " "),
                    InstructionTextToken(InstructionTextTokenType.RegisterToken, reg_name(info.a)),
                    InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ", "),
                    InstructionTextToken(InstructionTextTokenType.RegisterToken, reg_name(info.b)),
                    InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ", "),
                    InstructionTextToken(InstructionTextTokenType.RegisterToken, 'cc3'),
                ])
            case QuarkOpcode.mulx | QuarkOpcode.imulx:
                tokens.extend([
                    InstructionTextToken(InstructionTextTokenType.InstructionToken, op.name),
                    InstructionTextToken(InstructionTextTokenType.TextToken, " "),
                    InstructionTextToken(InstructionTextTokenType.RegisterToken, reg_name(info.d)),
                    InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ":"),
                    InstructionTextToken(InstructionTextTokenType.RegisterToken, reg_name(info.a)),
                    InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ", "),
                    InstructionTextToken(InstructionTextTokenType.RegisterToken, reg_name(info.b)),
                    InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ", "),
                    InstructionTextToken(InstructionTextTokenType.RegisterToken, reg_name(info.c)),
                ])
            case QuarkOpcode.syscall:
                tokens.extend([
                    InstructionTextToken(InstructionTextTokenType.InstructionToken, op.name),
                    InstructionTextToken(InstructionTextTokenType.TextToken, " "),
                    InstructionTextToken(InstructionTextTokenType.IntegerToken, f"{info.imm22}", value=info.imm22),
                ])
            case QuarkOpcode.integer_group:
                int_op = QuarkIntegerOpcode(info.b)
                match int_op:
                    case QuarkIntegerOpcode.mov:
                        tokens.extend([
                            InstructionTextToken(InstructionTextTokenType.InstructionToken, int_op.name),
                            InstructionTextToken(InstructionTextTokenType.TextToken, " "),
                            InstructionTextToken(InstructionTextTokenType.RegisterToken, reg_name(info.a)),
                            InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ", "),
                            *cval_tokens(plus=False, zero=False, signed=True),
                        ])
                    case QuarkIntegerOpcode.xchg | QuarkIntegerOpcode.sxb | QuarkIntegerOpcode.sxh | QuarkIntegerOpcode.swaph | QuarkIntegerOpcode.swapw | QuarkIntegerOpcode.neg | QuarkIntegerOpcode.not_ | QuarkIntegerOpcode.zxb | QuarkIntegerOpcode.zxh:
                        tokens.extend([
                            InstructionTextToken(InstructionTextTokenType.InstructionToken, int_op.name),
                            InstructionTextToken(InstructionTextTokenType.TextToken, " "),
                            InstructionTextToken(InstructionTextTokenType.RegisterToken, reg_name(info.a)),
                            InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ", "),
                            InstructionTextToken(InstructionTextTokenType.RegisterToken, reg_name(info.c)),
                        ])
                    case QuarkIntegerOpcode.call:
                        tokens.extend([
                            InstructionTextToken(InstructionTextTokenType.InstructionToken, int_op.name),
                            InstructionTextToken(InstructionTextTokenType.TextToken, " "),
                            InstructionTextToken(InstructionTextTokenType.RegisterToken, reg_name(info.a)),
                        ])
                    case QuarkIntegerOpcode.syscall:
                        tokens.extend([
                            InstructionTextToken(InstructionTextTokenType.InstructionToken, int_op.name),
                            InstructionTextToken(InstructionTextTokenType.TextToken, " "),
                            InstructionTextToken(InstructionTextTokenType.RegisterToken, reg_name(info.a)),
                        ])
                    case QuarkIntegerOpcode.ldcr | QuarkIntegerOpcode.stcr:
                        tokens.extend([
                            InstructionTextToken(InstructionTextTokenType.InstructionToken, int_op.name),
                            InstructionTextToken(InstructionTextTokenType.TextToken, " "),
                            InstructionTextToken(InstructionTextTokenType.RegisterToken, reg_name(info.a)),
                        ])
                    case QuarkIntegerOpcode.setcc | QuarkIntegerOpcode.clrcc:
                        tokens.extend([
                            InstructionTextToken(InstructionTextTokenType.InstructionToken, int_op.name),
                            InstructionTextToken(InstructionTextTokenType.TextToken, " "),
                            InstructionTextToken(InstructionTextTokenType.RegisterToken, f"cc{(info.a & 3)}"),
                        ])
                    case QuarkIntegerOpcode.notcc | QuarkIntegerOpcode.movcc:
                        tokens.extend([
                            InstructionTextToken(InstructionTextTokenType.InstructionToken, int_op.name),
                            InstructionTextToken(InstructionTextTokenType.TextToken, " "),
                            InstructionTextToken(InstructionTextTokenType.RegisterToken, f"cc{(info.a & 3)}"),
                            InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ", "),
                            InstructionTextToken(InstructionTextTokenType.RegisterToken, f"cc{(info.c & 3)}"),
                        ])
                    case QuarkIntegerOpcode.andcc | QuarkIntegerOpcode.orcc | QuarkIntegerOpcode.xorcc:
                        tokens.extend([
                            InstructionTextToken(InstructionTextTokenType.InstructionToken, int_op.name),
                            InstructionTextToken(InstructionTextTokenType.TextToken, " "),
                            InstructionTextToken(InstructionTextTokenType.RegisterToken, f"cc{(info.a & 3)}"),
                            InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ", "),
                            InstructionTextToken(InstructionTextTokenType.RegisterToken, f"cc{(info.c & 3)}"),
                            InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ", "),
                            InstructionTextToken(InstructionTextTokenType.RegisterToken, f"cc{(info.d & 3)}"),
                        ])
                    case _:
                        tokens.extend([InstructionTextToken(InstructionTextTokenType.InstructionToken, "??")])
            case QuarkOpcode.cmp | QuarkOpcode.icmp:
                cmp_op = QuarkCompareOpcode(info.b & 7)
                tokens.extend([
                    InstructionTextToken(InstructionTextTokenType.InstructionToken, f"{op.name}.{cmp_op.name}."),
                    InstructionTextToken(InstructionTextTokenType.RegisterToken, f"cc{info.b >> 3}"),
                    InstructionTextToken(InstructionTextTokenType.TextToken, " "),
                    InstructionTextToken(InstructionTextTokenType.RegisterToken, reg_name(info.a)),
                    InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ", "),
                    *cval_tokens(plus=False, zero=True, signed=True),
                ])
            case _:
                tokens.extend([InstructionTextToken(InstructionTextTokenType.InstructionToken, "??")])

        return tokens, 4

    def get_instruction_low_level_il(self, data: bytes, addr: int, il: LowLevelILFunction) -> Optional[int]:
        info = QuarkInstruction(int.from_bytes(data, 'little'))
        try:
            op = QuarkOpcode(info.op)
        except ValueError:
            print(f"Invalid opcode {info.op:#x} at {addr:#x} {data}")
            return None

        def ra():
            assert info.a != self.ip_reg_index, "Can't handle ip"
            return il.arch.get_reg_name(info.a)

        def rb():
            assert info.b != self.ip_reg_index, "Can't handle ip"
            return il.arch.get_reg_name(info.b)

        def rc():
            assert info.c != self.ip_reg_index, "Can't handle ip"
            return il.arch.get_reg_name(info.c)

        def rd():
            assert info.d != self.ip_reg_index, "Can't handle ip"
            return il.arch.get_reg_name(info.d)

        def ra_expr():
            if info.a == self.ip_reg_index:  # ip
                return il.const(4, addr + 4)
            return il.reg(4, il.arch.get_reg_name(info.a))

        def rb_expr():
            if info.b == self.ip_reg_index:  # ip
                return il.const(4, addr + 4)
            return il.reg(4, il.arch.get_reg_name(info.b))

        def rc_expr():
            if info.c == self.ip_reg_index:  # ip
                return il.const(4, addr + 4)
            return il.reg(4, il.arch.get_reg_name(info.c))

        def rd_expr():
            if info.d == self.ip_reg_index:  # ip
                return il.const(4, addr + 4)
            return il.reg(4, il.arch.get_reg_name(info.d))

        def cval():
            if info.largeimm:
                return il.const(4, info.imm11)
            elif info.smallimm:
                return il.const(4, rol(info.imm5, info.d))
            else:
                if info.d == 0:
                    return rc_expr()
                il.append(il.set_reg(4, LLIL_TEMP(0), il.shift_left(4, rc_expr(), il.const(4, info.d))))
                return il.reg(4, LLIL_TEMP(0))

        after = None
        if info.cond & 8:
            # Conditionally executed
            # TODO: Can we combine with the jmp instruction for jmpcc or equivalent
            # TODO: This should use flags
            before = LowLevelILLabel()
            after = LowLevelILLabel()
            il.append(
                il.if_expr(
                    il.compare_equal(
                        0,
                        il.flag(f"cc{(info.cond >> 1) & 3}"),
                        il.const(0, info.cond & 1)
                    ),
                    before,
                    after
                )
            )
            il.mark_label(before)
        elif info.cond & 1:
            # Always skipped apparently
            il.append(il.nop())
            return 4

        match op:
            case QuarkOpcode.ldb:
                il.append(il.set_reg(4, ra(), il.zero_extend(4, il.load(1, il.add(4, rb_expr(), cval())))))
            case QuarkOpcode.ldh:
                il.append(il.set_reg(4, ra(), il.zero_extend(4, il.load(2, il.add(4, rb_expr(), cval())))))
            case QuarkOpcode.ldw:
                il.append(il.set_reg(4, ra(), il.load(4, il.add(4, rb_expr(), cval()))))
            case QuarkOpcode.ldbu:
                addr = LLIL_TEMP(1)
                il.append(il.set_reg(4, addr, il.add(4, rb_expr(), cval())))
                il.append(il.set_reg(4, rb(), il.add(4, il.reg(4, addr), il.const(4, 1))))
                il.append(il.set_reg(4, ra(), il.zero_extend(4, il.load(1, il.reg(4, addr)))))
            case QuarkOpcode.ldhu:
                addr = LLIL_TEMP(1)
                il.append(il.set_reg(4, addr, il.add(4, rb_expr(), cval())))
                il.append(il.set_reg(4, rb(), il.add(4, il.reg(4, addr), il.const(4, 2))))
                il.append(il.set_reg(4, ra(), il.zero_extend(4, il.load(2, il.reg(4, addr)))))
            case QuarkOpcode.ldwu:
                addr = LLIL_TEMP(1)
                il.append(il.set_reg(4, addr, il.add(4, rb_expr(), cval())))
                il.append(il.set_reg(4, rb(), il.add(4, il.reg(4, addr), il.const(4, 4))))
                il.append(il.set_reg(4, ra(), il.load(4, il.reg(4, addr))))
            case QuarkOpcode.ldmw:
                addr = LLIL_TEMP(1)
                # (= addr (+ rb + cval))
                il.append(il.set_reg(4, addr, il.add(4, rb_expr(), cval())))
                for i in range(info.a, 31):
                    # (= temp2 (+ addr [(i-a) * 4])
                    il.append(il.set_reg(4, LLIL_TEMP(2), il.add(4, il.reg(4, addr), il.const(4, (i - info.a) * 4))))
                    # (= (reg i) (load (temp2))
                    il.append(il.set_reg(4, il.arch.get_reg_name(i), il.load(4, il.reg(4, LLIL_TEMP(2)))))
            case QuarkOpcode.ldmwu:
                addr = LLIL_TEMP(1)
                # (= addr (+ rb + cval))
                il.append(il.set_reg(4, addr, il.add(4, rb_expr(), cval())))
                # (= rb (+ addr [(31 - a) * 4]))
                il.append(il.set_reg(4, rb(), il.add(4, il.reg(4, addr), il.const(4, (31 - info.a) * 4))))
                for i in range(info.a, 31):
                    # (= temp2 (+ addr [(i-a) * 4])
                    il.append(il.set_reg(4, LLIL_TEMP(2), il.add(4, il.reg(4, addr), il.const(4, (i - info.a) * 4))))
                    # (= (reg i) (load (temp2))
                    il.append(il.set_reg(4, il.arch.get_reg_name(i), il.load(4, il.reg(4, LLIL_TEMP(2)))))
            case QuarkOpcode.ldsxb:
                il.append(il.set_reg(4, ra(), il.sign_extend(4, il.load(1, il.add(4, rb_expr(), cval())))))
            case QuarkOpcode.ldsxh:
                il.append(il.set_reg(4, ra(), il.sign_extend(4, il.load(2, il.add(4, rb_expr(), cval())))))
            case QuarkOpcode.ldsxbu:
                addr = LLIL_TEMP(1)
                il.append(il.set_reg(4, addr, il.add(4, rb_expr(), cval())))
                il.append(il.set_reg(4, rb(), il.add(4, il.reg(4, addr), il.const(4, 1))))
                il.append(il.set_reg(4, ra(), il.sign_extend(4, il.load(1, il.reg(4, addr)))))
            case QuarkOpcode.ldsxhu:
                addr = LLIL_TEMP(1)
                il.append(il.set_reg(4, addr, il.add(4, rb_expr(), cval())))
                il.append(il.set_reg(4, rb(), il.add(4, il.reg(4, addr), il.const(4, 1))))
                il.append(il.set_reg(4, ra(), il.sign_extend(4, il.load(2, il.reg(4, addr)))))
            case QuarkOpcode.ldi:
                il.append(il.set_reg(4, ra(), il.const(4, info.imm17)))
            case QuarkOpcode.ldih:
                il.append(il.set_reg(4, ra(), il.or_expr(4, ra_expr(), il.const(4, info.immhi))))
            case QuarkOpcode.stb:
                il.append(il.store(1, il.add(4, rb_expr(), cval()), il.low_part(1, ra_expr())))
            case QuarkOpcode.sth:
                il.append(il.store(2, il.add(4, rb_expr(), cval()), il.low_part(2, ra_expr())))
            case QuarkOpcode.stw:
                il.append(il.store(4, il.add(4, rb_expr(), cval()), ra_expr()))
            case QuarkOpcode.stbu:
                addr = LLIL_TEMP(1)
                il.append(il.set_reg(4, addr, il.add(4, rb_expr(), cval())))
                il.append(il.set_reg(4, rb(), il.reg(4, addr)))
                il.append(il.store(1, il.reg(4, addr), il.low_part(1, ra_expr())))
            case QuarkOpcode.sthu:
                addr = LLIL_TEMP(1)
                il.append(il.set_reg(4, addr, il.add(4, rb_expr(), cval())))
                il.append(il.set_reg(4, rb(), il.reg(4, addr)))
                il.append(il.store(2, il.reg(4, addr), il.low_part(2, ra_expr())))
            case QuarkOpcode.stwu:
                addr = LLIL_TEMP(1)
                il.append(il.set_reg(4, addr, il.add(4, rb_expr(), cval())))
                il.append(il.set_reg(4, rb(), il.reg(4, addr)))
                il.append(il.store(4, il.reg(4, addr), ra_expr()))
            case QuarkOpcode.stmw:
                addr = LLIL_TEMP(1)
                # (= addr (+ rb + cval))
                il.append(il.set_reg(4, addr, il.add(4, rb_expr(), cval())))
                for i in range(info.a, 31):
                    # (= temp2 (+ addr [(i-a) * 4])
                    il.append(il.set_reg(4, LLIL_TEMP(2), il.add(4, il.reg(4, addr), il.const(4, (i - info.a) * 4))))
                    # (store temp2 (reg i))
                    il.append(il.store(4, il.reg(4, LLIL_TEMP(2)), il.reg(4, il.arch.get_reg_name(i))))
            case QuarkOpcode.stmwu:
                addr = LLIL_TEMP(1)
                # (= addr (+ rb + cval))
                il.append(il.set_reg(4, addr, il.add(4, rb_expr(), cval())))
                for i in range(info.a, 31):
                    # (= temp2 (+ addr [(i-a) * 4])
                    il.append(il.set_reg(4, LLIL_TEMP(2), il.add(4, il.reg(4, addr), il.const(4, (i - info.a) * 4))))
                    # (store temp2 (reg i))
                    il.append(il.store(4, il.reg(4, LLIL_TEMP(2)), il.reg(4, il.arch.get_reg_name(i))))
                # (= rb addr)
                il.append(il.set_reg(4, rb(), il.reg(4, addr)))
            case QuarkOpcode.jmp:
                il.append(il.jump(il.const(4, addr + 4 + (info.imm22 << 2))))
            case QuarkOpcode.call:
                il.append(il.call(il.const(4, addr + 4 + (info.imm22 << 2))))
            case QuarkOpcode.add:
                il.append(il.set_reg(4, ra(), il.add(4, rb_expr(), cval())))
            case QuarkOpcode.sub:
                il.append(il.set_reg(4, ra(), il.sub(4, rb_expr(), cval())))
            case QuarkOpcode.addx:
                il.append(il.set_reg(4, ra(), il.add_carry(4, rb_expr(), cval(), il.flag('cc3'), flags='3')))
            case QuarkOpcode.subx:
                il.append(il.set_reg(4, ra(), il.sub_borrow(4, rb_expr(), cval(), il.flag('cc3'), flags='3')))
            case QuarkOpcode.mulx:
                il.append(il.set_reg_split(4, rd(), ra(), il.mult_double_prec_unsigned(4, rb_expr(), rc_expr())))
            case QuarkOpcode.imulx:
                il.append(il.set_reg_split(4, rd(), ra(), il.mult_double_prec_signed(4, rb_expr(), rc_expr())))
            case QuarkOpcode.mul:
                il.append(il.set_reg(4, ra(), il.mult(4, rb_expr(), cval())))
            case QuarkOpcode.div:
                il.append(il.set_reg(4, ra(), il.div_unsigned(4, rb_expr(), cval())))
            case QuarkOpcode.idiv:
                il.append(il.set_reg(4, ra(), il.div_signed(4, rb_expr(), cval())))
            case QuarkOpcode.mod:
                il.append(il.set_reg(4, ra(), il.mod_unsigned(4, rb_expr(), cval())))
            case QuarkOpcode.imod:
                il.append(il.set_reg(4, ra(), il.mod_signed(4, rb_expr(), cval())))
            case QuarkOpcode.and_:
                il.append(il.set_reg(4, ra(), il.and_expr(4, rb_expr(), cval())))
            case QuarkOpcode.or_:
                il.append(il.set_reg(4, ra(), il.or_expr(4, rb_expr(), cval())))
            case QuarkOpcode.xor:
                il.append(il.set_reg(4, ra(), il.xor_expr(4, rb_expr(), cval())))
            case QuarkOpcode.sar:
                il.append(il.set_reg(4, ra(), il.arith_shift_right(4, rb_expr(), cval())))
            case QuarkOpcode.shl:
                il.append(il.set_reg(4, ra(), il.shift_left(4, rb_expr(), cval())))
            case QuarkOpcode.shr:
                il.append(il.set_reg(4, ra(), il.logical_shift_right(4, rb_expr(), cval())))
            case QuarkOpcode.rol:
                il.append(il.set_reg(4, ra(), il.rotate_left(4, rb_expr(), cval())))
            case QuarkOpcode.ror:
                il.append(il.set_reg(4, ra(), il.rotate_right(4, rb_expr(), cval())))
            case QuarkOpcode.syscall:
                il.append(il.set_reg(4, 'syscall_num', il.const(4, info.imm22)))
                il.append(il.system_call())
            case QuarkOpcode.integer_group:
                int_op = QuarkIntegerOpcode(info.b)
                match int_op:
                    case QuarkIntegerOpcode.mov:
                        if info.a == 31:
                            il.append(il.jump(cval()))
                        else:
                            il.append(il.set_reg(4, ra(), cval()))
                    case QuarkIntegerOpcode.xchg:
                        result = LLIL_TEMP(1)
                        il.append(il.set_reg(4, result, ra_expr()))
                        il.append(il.set_reg(4, ra(), rc_expr()))
                        il.append(il.set_reg(4, rc(), il.reg(4, result)))
                    case QuarkIntegerOpcode.sxb:
                        il.append(il.set_reg(4, ra(), il.sign_extend(4, il.low_part(1, rc_expr()))))
                    case QuarkIntegerOpcode.sxh:
                        il.append(il.set_reg(4, ra(), il.sign_extend(4, il.low_part(2, rc_expr()))))
                    case QuarkIntegerOpcode.swaph:
                        il.append(il.intrinsic([ra()], '__byteswaph', [il.low_part(2, rc_expr())]))
                    case QuarkIntegerOpcode.swapw:
                        il.append(il.intrinsic([ra()], '__byteswapw', [rc_expr()]))
                    case QuarkIntegerOpcode.call:
                        addr = LLIL_TEMP(1)
                        il.append(il.set_reg(4, addr, ra_expr()))
                        il.append(il.call(il.reg(4, addr)))
                    case QuarkIntegerOpcode.neg:
                        il.append(il.set_reg(4, ra(), il.neg_expr(4, rc_expr())))
                    case QuarkIntegerOpcode.not_:
                        il.append(il.set_reg(4, ra(), il.not_expr(4, rc_expr())))
                    case QuarkIntegerOpcode.zxb:
                        il.append(il.set_reg(4, ra(), il.zero_extend(4, il.low_part(1, rc_expr()))))
                    case QuarkIntegerOpcode.zxh:
                        il.append(il.set_reg(4, ra(), il.zero_extend(4, il.low_part(2, rc_expr()))))
                    case QuarkIntegerOpcode.ldcr:
                        cc0 = il.flag_bit(4, 'cc0', 0)
                        cc1 = il.flag_bit(4, 'cc1', 8)
                        cc2 = il.flag_bit(4, 'cc2', 16)
                        cc3 = il.flag_bit(4, 'cc3', 24)
                        il.append(il.set_reg(4, ra(), il.or_expr(4, cc3, il.or_expr(4, cc2, il.or_expr(4, cc1, cc0)))))
                    case QuarkIntegerOpcode.stcr:
                        il.append(il.set_reg(1, LLIL_TEMP(0), ra_expr()))
                        il.append(il.set_flag('cc0', il.test_bit(4, il.reg(4, LLIL_TEMP(0)), il.const(4, 0x1))))
                        il.append(il.set_flag('cc1', il.test_bit(4, il.reg(4, LLIL_TEMP(0)), il.const(4, 0x100))))
                        il.append(il.set_flag('cc2', il.test_bit(4, il.reg(4, LLIL_TEMP(0)), il.const(4, 0x10000))))
                        il.append(il.set_flag('cc3', il.test_bit(4, il.reg(4, LLIL_TEMP(0)), il.const(4, 0x1000000))))
                    case QuarkIntegerOpcode.syscall:
                        il.append(il.set_reg(4, 'syscall_num', ra_expr()))
                        il.append(il.system_call())
                    case QuarkIntegerOpcode.setcc:
                        il.append(il.set_flag(il.arch.get_flag_index(f"cc{info.a & 3}"), il.const(0, 1)))
                    case QuarkIntegerOpcode.clrcc:
                        il.append(il.set_flag(il.arch.get_flag_index(f"cc{info.a & 3}"), il.const(0, 0)))
                    case QuarkIntegerOpcode.notcc:
                        il.append(il.set_flag(il.arch.get_flag_index(f"cc{info.a & 3}"), il.not_expr(0, il.flag(f"cc{info.c & 3}"))))
                    case QuarkIntegerOpcode.movcc:
                        il.append(il.set_flag(il.arch.get_flag_index(f"cc{info.a & 3}"), il.flag(f"cc{info.c & 3}")))
                    case QuarkIntegerOpcode.andcc:
                        il.append(il.set_flag(il.arch.get_flag_index(f"cc{info.a & 3}"), il.and_expr(0, il.flag(f"cc{info.c & 3}"), il.flag(f"cc{info.d & 3}"))))
                    case QuarkIntegerOpcode.orcc:
                        il.append(il.set_flag(il.arch.get_flag_index(f"cc{info.a & 3}"), il.or_expr(0, il.flag(f"cc{info.c & 3}"), il.flag(f"cc{info.d & 3}"))))
                    case QuarkIntegerOpcode.xorcc:
                        il.append(il.set_flag(il.arch.get_flag_index(f"cc{info.a & 3}"), il.xor_expr(0, il.flag(f"cc{info.c & 3}"), il.flag(f"cc{info.d & 3}"))))
                    case _:
                        il.append(il.unimplemented())
            case QuarkOpcode.cmp:
                cmp_op = QuarkCompareOpcode(info.b & 7)
                match cmp_op:
                    case QuarkCompareOpcode.lt:
                        il.append(il.set_flag(il.arch.get_flag_index(f"cc{info.b >> 3}"), il.compare_unsigned_less_than(4, ra_expr(), cval())))
                    case QuarkCompareOpcode.le:
                        il.append(il.set_flag(il.arch.get_flag_index(f"cc{info.b >> 3}"), il.compare_unsigned_less_equal(4, ra_expr(), cval())))
                    case QuarkCompareOpcode.ge:
                        il.append(il.set_flag(il.arch.get_flag_index(f"cc{info.b >> 3}"), il.compare_unsigned_greater_equal(4, ra_expr(), cval())))
                    case QuarkCompareOpcode.gt:
                        il.append(il.set_flag(il.arch.get_flag_index(f"cc{info.b >> 3}"), il.compare_unsigned_greater_than(4, ra_expr(), cval())))
                    case QuarkCompareOpcode.eq:
                        il.append(il.set_flag(il.arch.get_flag_index(f"cc{info.b >> 3}"), il.compare_equal(4, ra_expr(), cval())))
                    case QuarkCompareOpcode.ne:
                        il.append(il.set_flag(il.arch.get_flag_index(f"cc{info.b >> 3}"), il.compare_not_equal(4, ra_expr(), cval())))
                    case QuarkCompareOpcode.nz | QuarkCompareOpcode.z:
                        il.append(il.and_expr(4, ra_expr(), cval(), flags=str(info.b >> 3)))
                    case _:
                        il.append(il.unimplemented())
            case QuarkOpcode.icmp:
                cmp_op = QuarkCompareOpcode(info.b & 7)
                match cmp_op:
                    case QuarkCompareOpcode.lt:
                        il.append(il.set_flag(il.arch.get_flag_index(f"cc{info.b >> 3}"), il.compare_signed_less_than(4, ra_expr(), cval())))
                    case QuarkCompareOpcode.le:
                        il.append(il.set_flag(il.arch.get_flag_index(f"cc{info.b >> 3}"), il.compare_signed_less_equal(4, ra_expr(), cval())))
                    case QuarkCompareOpcode.ge:
                        il.append(il.set_flag(il.arch.get_flag_index(f"cc{info.b >> 3}"), il.compare_signed_greater_equal(4, ra_expr(), cval())))
                    case QuarkCompareOpcode.gt:
                        il.append(il.set_flag(il.arch.get_flag_index(f"cc{info.b >> 3}"), il.compare_signed_greater_than(4, ra_expr(), cval())))
                    case QuarkCompareOpcode.eq:
                        il.append(il.set_flag(il.arch.get_flag_index(f"cc{info.b >> 3}"), il.compare_equal(4, ra_expr(), cval())))
                    case QuarkCompareOpcode.ne:
                        il.append(il.set_flag(il.arch.get_flag_index(f"cc{info.b >> 3}"), il.compare_not_equal(4, ra_expr(), cval())))
                    case QuarkCompareOpcode.nz | QuarkCompareOpcode.z:
                        il.append(il.and_expr(4, ra_expr(), cval(), flags=str(info.b >> 3)))
                    case _:
                        il.append(il.unimplemented())
            case _:
                il.append(il.unimplemented())

        if after is not None:
            il.mark_label(after)

        return 4

    def get_flag_write_low_level_il(
        self, op: LowLevelILOperation, size: int, write_type: Optional[FlagWriteTypeName], flag: FlagType,
        operands: List['ILRegisterType'], il: 'LowLevelILFunction'
    ) -> 'ExpressionIndex':
        print(f"get_flag_write_low_level_il: {op} {size} {write_type} {flag} {operands}")
        return il.unimplemented()


class QuarkCallingConvention(CallingConvention):
    name = "qcall"
    caller_saved_regs = ['r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9', 'r10', 'r11', 'r12', 'r13', 'r14', 'r15']
    callee_saved_regs = ['r16', 'r17', 'r18', 'r19', 'r20', 'r21', 'r22', 'r23', 'r24', 'r25', 'r26', 'r27', 'r28']
    int_arg_regs = ['r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8']
    int_return_reg = 'r1'
    high_int_return_reg = 'r2'
    stack_reserved_for_arg_regs = True


class QuarkSyscallCallingConvention(CallingConvention):
    name = "qsyscall"
    caller_saved_regs = ['r1', 'r2']
    callee_saved_regs = ['r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9', 'r10', 'r11', 'r12', 'r13', 'r14', 'r15', 'r16', 'r17', 'r18', 'r19', 'r20', 'r21', 'r22', 'r23', 'r24', 'r25', 'r26', 'r27', 'r28']
    int_arg_regs = ['syscall_num', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8']
    int_return_reg = 'r1'
    high_int_return_reg = 'r2'
    stack_reserved_for_arg_regs = True
    eligible_for_heuristics = False


class LinuxQuarkPlatform(Platform):
    name = "linux-quark"


QuarkArch.register()
qarch = Architecture['Quark']

qcc = QuarkCallingConvention(qarch, "qcall")
qarch.register_calling_convention(qcc)
qarch.default_calling_convention = qcc

qsyscall = QuarkSyscallCallingConvention(qarch, "qsyscall")
qarch.register_calling_convention(qsyscall)

qlinuxplatform = LinuxQuarkPlatform(qarch)
qlinuxplatform.register_calling_convention(qcc)
qlinuxplatform.register_calling_convention(qsyscall)
qlinuxplatform.default_calling_convention = qcc
qlinuxplatform.system_call_convention = qsyscall
qlinuxplatform.register("linux")

BinaryViewType['ELF'].register_arch(4242, Endianness.LittleEndian, qarch)
BinaryViewType['ELF'].register_platform(0, qarch, qlinuxplatform)
BinaryViewType['ELF'].register_platform(3, qarch, qlinuxplatform)

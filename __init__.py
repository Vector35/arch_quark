import enum
import json
import math
from pathlib import Path
from typing import Optional, Tuple, List

import binaryninja
from binaryninja import Architecture, RegisterInfo, InstructionInfo, InstructionTextToken, \
    InstructionTextTokenType, BinaryViewType, Endianness, BranchType, lowlevelil, \
    LowLevelILLabel, LowLevelILFunction, LLIL_TEMP, FlagRole, LowLevelILOperation, \
    FlagWriteTypeName, FlagType, ILRegisterType, IntrinsicInfo, Type, \
    IntrinsicInput, CallingConvention, Platform, ILRegister, Workflow, AnalysisContext, \
    Activity, LowLevelILInstruction, LowLevelILSetReg, LowLevelILAdd, ILSourceLocation, \
    TypeLibrary, BinaryView, LowLevelILFlagCondition, SemanticGroupType
from binaryninja.lowlevelil import ExpressionIndex, ILFlag, InstructionIndex, \
    LowLevelILConst, LowLevelILReg
from binaryninja.warp import WarpContainer


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

    # These are all unimplemented by defined by the spec
    # fcmp = 0x2f
    # ldfs = 0x30
    # ldfd = 0x31
    # stfs = 0x32
    # stfd = 0x33
    # ldfsu = 0x34
    # ldfdu = 0x35
    # stfsu = 0x36
    # stfdu = 0x37
    # fadd = 0x38
    # fsub = 0x39
    # fmul = 0x3a
    # fdiv = 0x3b
    # fmod = 0x3c
    # fpow = 0x3d
    # flog = 0x3e
    # float_group = 0x3f


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
    # Unimplemented but defined
    bp = 0x1f


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

    def __repr__(self):
        return f"QuarkInstruction({self.cond=} {self.op=} {self.a=} {self.b=} {self.c=} {self.d=} {self.imm5=} {self.imm11=} {self.imm17=} {self.imm22=} {self.immhi=} {self.smallimm=} {self.largeimm=})"

    @property
    def cond(self):
        return self.instr >> 28

    @cond.setter
    def cond(self, cond):
        self.instr = (self.instr & 0b0000_1111_1111_1111_1111_1111_1111_1111) | ((cond & 0xf) << 28)

    @property
    def op(self):
        return (self.instr >> 22) & 0x3f

    @op.setter
    def op(self, op):
        self.instr = (self.instr & 0b1111_0000_0011_1111_1111_1111_1111_1111) | ((op & 0x3f) << 22)

    @property
    def a(self):
        return (self.instr >> 17) & 0x1f

    @a.setter
    def a(self, a):
        self.instr = (self.instr & 0b1111_1111_1100_0001_1111_1111_1111_1111) | ((a & 0x1f) << 17)

    @property
    def b(self):
        return (self.instr >> 12) & 0x1f

    @b.setter
    def b(self, b):
        self.instr = (self.instr & 0b1111_1111_1111_1110_0000_1111_1111_1111) | ((b & 0x1f) << 12)

    @property
    def c(self):
        return (self.instr >> 5) & 0x1f

    @c.setter
    def c(self, c):
        self.instr = (self.instr & 0b1111_1111_1111_1111_1111_1100_0001_1111) | ((c & 0x1f) << 5)

    @property
    def d(self):
        return self.instr & 0x1f

    @d.setter
    def d(self, d):
        self.instr = (self.instr & 0b1111_1111_1111_1111_1111_1111_1110_0000) | (d & 0x1f)

    @property
    def imm5(self):
        if self.instr & 0x10:
            return (self.instr & 0x1f) | 0xffffffe0
        return self.instr & 0x1f

    @imm5.setter
    def imm5(self, imm5):
        if imm5 < 0:
            # 2s complement with 32 bit
            imm5 = 0x100000000 + imm5
        self.instr = (self.instr & 0b1111_1111_1111_1111_1111_1111_1110_0000) | (imm5 & 0x1f)

    @property
    def imm11(self):
        if self.instr & 0x400:
            return (self.instr & 0x7ff) | 0xfffff800
        return self.instr & 0x7ff

    @imm11.setter
    def imm11(self, imm11):
        if imm11 < 0:
            imm11 = 0x100000000 + imm11
        self.instr = (self.instr & 0b1111_1111_1111_1111_1111_1000_0000_0000) | (imm11 & 0x7ff)

    @property
    def imm17(self):
        if self.instr & 0x10000:
            return (self.instr & 0x1ffff) | 0xfffe0000
        return self.instr & 0x1ffff

    @imm17.setter
    def imm17(self, imm17):
        if imm17 < 0:
            imm17 = 0x100000000 + imm17
        self.instr = (self.instr & 0b1111_1111_1111_1110_0000_0000_0000_0000) | (imm17 & 0x1ffff)

    @property
    def imm22(self):
        if self.instr & 0x200000:
            return (self.instr & 0x3fffff) | 0xffc00000
        return self.instr & 0x3fffff

    @imm22.setter
    def imm22(self, imm22):
        if imm22 < 0:
            imm22 = 0x100000000 + imm22
        self.instr = (self.instr & 0b1111_1111_1100_0000_0000_0000_0000_0000) | (imm22 & 0x3fffff)

    @property
    def immhi(self):
        return (self.instr & 0xffff) << 16

    @immhi.setter
    def immhi(self, immhi):
        self.instr = (self.instr & 0b1111_1111_1111_1111_0000_0000_0000_0000) | ((immhi & 0xffff0000) >> 16)

    @property
    def smallimm(self):
        return True if self.instr & 0x400 else False

    @smallimm.setter
    def smallimm(self, smallimm):
        self.instr = (self.instr & 0b1111_1111_1111_1111_1111_1011_1111_1111) | (0x400 if smallimm else 0)

    @property
    def largeimm(self):
        return True if self.instr & 0x800 else False

    @largeimm.setter
    def largeimm(self, largeimm):
        self.instr = (self.instr & 0b1111_1111_1111_1111_1111_0111_1111_1111) | (0x800 if largeimm else 0)


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
    semantic_flag_classes = [
        'cc0.cmp.lt',  'cc0.cmp.le',  'cc0.cmp.ge',  'cc0.cmp.gt',  'cc0.cmp.eq',  'cc0.cmp.ne',  'cc0.cmp.z',  'cc0.cmp.nz',
        'cc0.icmp.lt', 'cc0.icmp.le', 'cc0.icmp.ge', 'cc0.icmp.gt', 'cc0.icmp.eq', 'cc0.icmp.ne', 'cc0.icmp.z', 'cc0.icmp.nz',
        'cc1.cmp.lt',  'cc1.cmp.le',  'cc1.cmp.ge',  'cc1.cmp.gt',  'cc1.cmp.eq',  'cc1.cmp.ne',  'cc1.cmp.z',  'cc1.cmp.nz',
        'cc1.icmp.lt', 'cc1.icmp.le', 'cc1.icmp.ge', 'cc1.icmp.gt', 'cc1.icmp.eq', 'cc1.icmp.ne', 'cc1.icmp.z', 'cc1.icmp.nz',
        'cc2.cmp.lt',  'cc2.cmp.le',  'cc2.cmp.ge',  'cc2.cmp.gt',  'cc2.cmp.eq',  'cc2.cmp.ne',  'cc2.cmp.z',  'cc2.cmp.nz',
        'cc2.icmp.lt', 'cc2.icmp.le', 'cc2.icmp.ge', 'cc2.icmp.gt', 'cc2.icmp.eq', 'cc2.icmp.ne', 'cc2.icmp.z', 'cc2.icmp.nz',
        'cc3.cmp.lt',  'cc3.cmp.le',  'cc3.cmp.ge',  'cc3.cmp.gt',  'cc3.cmp.eq',  'cc3.cmp.ne',  'cc3.cmp.z',  'cc3.cmp.nz',
        'cc3.icmp.lt', 'cc3.icmp.le', 'cc3.icmp.ge', 'cc3.icmp.gt', 'cc3.icmp.eq', 'cc3.icmp.ne', 'cc3.icmp.z', 'cc3.icmp.nz',
    ]
    semantic_flag_groups = [
        'cc0',
        'cc1',
        'cc2',
        'cc3',
    ]
    flags_required_for_semantic_flag_group = {
        'cc0': ['cc0'],
        'cc1': ['cc1'],
        'cc2': ['cc2'],
        'cc3': ['cc3'],
    }
    flag_conditions_for_semantic_flag_group = {
        'cc0': {
            'cc0.cmp.lt': LowLevelILFlagCondition.LLFC_ULT,
            'cc0.cmp.le': LowLevelILFlagCondition.LLFC_ULE,
            'cc0.cmp.ge': LowLevelILFlagCondition.LLFC_UGE,
            'cc0.cmp.gt': LowLevelILFlagCondition.LLFC_UGT,
            'cc0.cmp.eq': LowLevelILFlagCondition.LLFC_E,
            'cc0.cmp.ne': LowLevelILFlagCondition.LLFC_NE,
            'cc0.icmp.lt': LowLevelILFlagCondition.LLFC_SLT,
            'cc0.icmp.le': LowLevelILFlagCondition.LLFC_SLE,
            'cc0.icmp.ge': LowLevelILFlagCondition.LLFC_SGE,
            'cc0.icmp.gt': LowLevelILFlagCondition.LLFC_SGT,
            'cc0.icmp.eq': LowLevelILFlagCondition.LLFC_E,
            'cc0.icmp.ne': LowLevelILFlagCondition.LLFC_NE,
        },
        'cc1': {
            'cc1.cmp.lt': LowLevelILFlagCondition.LLFC_ULT,
            'cc1.cmp.le': LowLevelILFlagCondition.LLFC_ULE,
            'cc1.cmp.ge': LowLevelILFlagCondition.LLFC_UGE,
            'cc1.cmp.gt': LowLevelILFlagCondition.LLFC_UGT,
            'cc1.cmp.eq': LowLevelILFlagCondition.LLFC_E,
            'cc1.cmp.ne': LowLevelILFlagCondition.LLFC_NE,
            'cc1.icmp.lt': LowLevelILFlagCondition.LLFC_SLT,
            'cc1.icmp.le': LowLevelILFlagCondition.LLFC_SLE,
            'cc1.icmp.ge': LowLevelILFlagCondition.LLFC_SGE,
            'cc1.icmp.gt': LowLevelILFlagCondition.LLFC_SGT,
            'cc1.icmp.eq': LowLevelILFlagCondition.LLFC_E,
            'cc1.icmp.ne': LowLevelILFlagCondition.LLFC_NE,
        },
        'cc2': {
            'cc2.cmp.lt': LowLevelILFlagCondition.LLFC_ULT,
            'cc2.cmp.le': LowLevelILFlagCondition.LLFC_ULE,
            'cc2.cmp.ge': LowLevelILFlagCondition.LLFC_UGE,
            'cc2.cmp.gt': LowLevelILFlagCondition.LLFC_UGT,
            'cc2.cmp.eq': LowLevelILFlagCondition.LLFC_E,
            'cc2.cmp.ne': LowLevelILFlagCondition.LLFC_NE,
            'cc2.icmp.lt': LowLevelILFlagCondition.LLFC_SLT,
            'cc2.icmp.le': LowLevelILFlagCondition.LLFC_SLE,
            'cc2.icmp.ge': LowLevelILFlagCondition.LLFC_SGE,
            'cc2.icmp.gt': LowLevelILFlagCondition.LLFC_SGT,
            'cc2.icmp.eq': LowLevelILFlagCondition.LLFC_E,
            'cc2.icmp.ne': LowLevelILFlagCondition.LLFC_NE,
        },
        'cc3': {
            'cc3.cmp.lt': LowLevelILFlagCondition.LLFC_ULT,
            'cc3.cmp.le': LowLevelILFlagCondition.LLFC_ULE,
            'cc3.cmp.ge': LowLevelILFlagCondition.LLFC_UGE,
            'cc3.cmp.gt': LowLevelILFlagCondition.LLFC_UGT,
            'cc3.cmp.eq': LowLevelILFlagCondition.LLFC_E,
            'cc3.cmp.ne': LowLevelILFlagCondition.LLFC_NE,
            'cc3.icmp.lt': LowLevelILFlagCondition.LLFC_SLT,
            'cc3.icmp.le': LowLevelILFlagCondition.LLFC_SLE,
            'cc3.icmp.ge': LowLevelILFlagCondition.LLFC_SGE,
            'cc3.icmp.gt': LowLevelILFlagCondition.LLFC_SGT,
            'cc3.icmp.eq': LowLevelILFlagCondition.LLFC_E,
            'cc3.icmp.ne': LowLevelILFlagCondition.LLFC_NE,
        },
    }
    semantic_class_for_flag_write_type = {
        'cc0.cmp.lt':  'cc0.cmp.lt',  'cc0.cmp.le':  'cc0.cmp.le',  'cc0.cmp.ge':  'cc0.cmp.ge',  'cc0.cmp.gt':  'cc0.cmp.gt',  'cc0.cmp.eq':  'cc0.cmp.eq',  'cc0.cmp.ne':  'cc0.cmp.ne',  'cc0.cmp.z':  'cc0.cmp.z',  'cc0.cmp.nz':  'cc0.cmp.nz',
        'cc0.icmp.lt': 'cc0.icmp.lt', 'cc0.icmp.le': 'cc0.icmp.le', 'cc0.icmp.ge': 'cc0.icmp.ge', 'cc0.icmp.gt': 'cc0.icmp.gt', 'cc0.icmp.eq': 'cc0.icmp.eq', 'cc0.icmp.ne': 'cc0.icmp.ne', 'cc0.icmp.z': 'cc0.icmp.z', 'cc0.icmp.nz': 'cc0.icmp.nz',
        'cc1.cmp.lt':  'cc1.cmp.lt',  'cc1.cmp.le':  'cc1.cmp.le',  'cc1.cmp.ge':  'cc1.cmp.ge',  'cc1.cmp.gt':  'cc1.cmp.gt',  'cc1.cmp.eq':  'cc1.cmp.eq',  'cc1.cmp.ne':  'cc1.cmp.ne',  'cc1.cmp.z':  'cc1.cmp.z',  'cc1.cmp.nz':  'cc1.cmp.nz',
        'cc1.icmp.lt': 'cc1.icmp.lt', 'cc1.icmp.le': 'cc1.icmp.le', 'cc1.icmp.ge': 'cc1.icmp.ge', 'cc1.icmp.gt': 'cc1.icmp.gt', 'cc1.icmp.eq': 'cc1.icmp.eq', 'cc1.icmp.ne': 'cc1.icmp.ne', 'cc1.icmp.z': 'cc1.icmp.z', 'cc1.icmp.nz': 'cc1.icmp.nz',
        'cc2.cmp.lt':  'cc2.cmp.lt',  'cc2.cmp.le':  'cc2.cmp.le',  'cc2.cmp.ge':  'cc2.cmp.ge',  'cc2.cmp.gt':  'cc2.cmp.gt',  'cc2.cmp.eq':  'cc2.cmp.eq',  'cc2.cmp.ne':  'cc2.cmp.ne',  'cc2.cmp.z':  'cc2.cmp.z',  'cc2.cmp.nz':  'cc2.cmp.nz',
        'cc2.icmp.lt': 'cc2.icmp.lt', 'cc2.icmp.le': 'cc2.icmp.le', 'cc2.icmp.ge': 'cc2.icmp.ge', 'cc2.icmp.gt': 'cc2.icmp.gt', 'cc2.icmp.eq': 'cc2.icmp.eq', 'cc2.icmp.ne': 'cc2.icmp.ne', 'cc2.icmp.z': 'cc2.icmp.z', 'cc2.icmp.nz': 'cc2.icmp.nz',
        'cc3.cmp.lt':  'cc3.cmp.lt',  'cc3.cmp.le':  'cc3.cmp.le',  'cc3.cmp.ge':  'cc3.cmp.ge',  'cc3.cmp.gt':  'cc3.cmp.gt',  'cc3.cmp.eq':  'cc3.cmp.eq',  'cc3.cmp.ne':  'cc3.cmp.ne',  'cc3.cmp.z':  'cc3.cmp.z',  'cc3.cmp.nz':  'cc3.cmp.nz',
        'cc3.icmp.lt': 'cc3.icmp.lt', 'cc3.icmp.le': 'cc3.icmp.le', 'cc3.icmp.ge': 'cc3.icmp.ge', 'cc3.icmp.gt': 'cc3.icmp.gt', 'cc3.icmp.eq': 'cc3.icmp.eq', 'cc3.icmp.ne': 'cc3.icmp.ne', 'cc3.icmp.z': 'cc3.icmp.z', 'cc3.icmp.nz': 'cc3.icmp.nz',
    }
    flag_write_types = {
        'none',
        'cc0.cmp.lt',  'cc0.cmp.le',  'cc0.cmp.ge',  'cc0.cmp.gt',  'cc0.cmp.eq',  'cc0.cmp.ne',  'cc0.cmp.z',  'cc0.cmp.nz',
        'cc0.icmp.lt', 'cc0.icmp.le', 'cc0.icmp.ge', 'cc0.icmp.gt', 'cc0.icmp.eq', 'cc0.icmp.ne', 'cc0.icmp.z', 'cc0.icmp.nz',
        'cc1.cmp.lt',  'cc1.cmp.le',  'cc1.cmp.ge',  'cc1.cmp.gt',  'cc1.cmp.eq',  'cc1.cmp.ne',  'cc1.cmp.z',  'cc1.cmp.nz',
        'cc1.icmp.lt', 'cc1.icmp.le', 'cc1.icmp.ge', 'cc1.icmp.gt', 'cc1.icmp.eq', 'cc1.icmp.ne', 'cc1.icmp.z', 'cc1.icmp.nz',
        'cc2.cmp.lt',  'cc2.cmp.le',  'cc2.cmp.ge',  'cc2.cmp.gt',  'cc2.cmp.eq',  'cc2.cmp.ne',  'cc2.cmp.z',  'cc2.cmp.nz',
        'cc2.icmp.lt', 'cc2.icmp.le', 'cc2.icmp.ge', 'cc2.icmp.gt', 'cc2.icmp.eq', 'cc2.icmp.ne', 'cc2.icmp.z', 'cc2.icmp.nz',
        'cc3.cmp.lt',  'cc3.cmp.le',  'cc3.cmp.ge',  'cc3.cmp.gt',  'cc3.cmp.eq',  'cc3.cmp.ne',  'cc3.cmp.z',  'cc3.cmp.nz',
        'cc3.icmp.lt', 'cc3.icmp.le', 'cc3.icmp.ge', 'cc3.icmp.gt', 'cc3.icmp.eq', 'cc3.icmp.ne', 'cc3.icmp.z', 'cc3.icmp.nz',
        'addx'
    }
    flags_written_by_flag_write_type = {
        'none': {},
        'cc0.cmp.lt' : ['cc0'],  'cc0.cmp.le' : ['cc0'],  'cc0.cmp.ge' : ['cc0'],  'cc0.cmp.gt' : ['cc0'],  'cc0.cmp.eq' : ['cc0'],  'cc0.cmp.ne' : ['cc0'],  'cc0.cmp.z' : ['cc0'],  'cc0.cmp.nz' : ['cc0'],
        'cc0.icmp.lt' : ['cc0'], 'cc0.icmp.le' : ['cc0'], 'cc0.icmp.ge' : ['cc0'], 'cc0.icmp.gt' : ['cc0'], 'cc0.icmp.eq' : ['cc0'], 'cc0.icmp.ne' : ['cc0'], 'cc0.icmp.z' : ['cc0'], 'cc0.icmp.nz' : ['cc0'],
        'cc1.cmp.lt' : ['cc1'],  'cc1.cmp.le' : ['cc1'],  'cc1.cmp.ge' : ['cc1'],  'cc1.cmp.gt' : ['cc1'],  'cc1.cmp.eq' : ['cc1'],  'cc1.cmp.ne' : ['cc1'],  'cc1.cmp.z' : ['cc1'],  'cc1.cmp.nz' : ['cc1'],
        'cc1.icmp.lt' : ['cc1'], 'cc1.icmp.le' : ['cc1'], 'cc1.icmp.ge' : ['cc1'], 'cc1.icmp.gt' : ['cc1'], 'cc1.icmp.eq' : ['cc1'], 'cc1.icmp.ne' : ['cc1'], 'cc1.icmp.z' : ['cc1'], 'cc1.icmp.nz' : ['cc1'],
        'cc2.cmp.lt' : ['cc2'],  'cc2.cmp.le' : ['cc2'],  'cc2.cmp.ge' : ['cc2'],  'cc2.cmp.gt' : ['cc2'],  'cc2.cmp.eq' : ['cc2'],  'cc2.cmp.ne' : ['cc2'],  'cc2.cmp.z' : ['cc2'],  'cc2.cmp.nz' : ['cc2'],
        'cc2.icmp.lt' : ['cc2'], 'cc2.icmp.le' : ['cc2'], 'cc2.icmp.ge' : ['cc2'], 'cc2.icmp.gt' : ['cc2'], 'cc2.icmp.eq' : ['cc2'], 'cc2.icmp.ne' : ['cc2'], 'cc2.icmp.z' : ['cc2'], 'cc2.icmp.nz' : ['cc2'],
        'cc3.cmp.lt' : ['cc3'],  'cc3.cmp.le' : ['cc3'],  'cc3.cmp.ge' : ['cc3'],  'cc3.cmp.gt' : ['cc3'],  'cc3.cmp.eq' : ['cc3'],  'cc3.cmp.ne' : ['cc3'],  'cc3.cmp.z' : ['cc3'],  'cc3.cmp.nz' : ['cc3'],
        'cc3.icmp.lt' : ['cc3'], 'cc3.icmp.le' : ['cc3'], 'cc3.icmp.ge' : ['cc3'], 'cc3.icmp.gt' : ['cc3'], 'cc3.icmp.eq' : ['cc3'], 'cc3.icmp.ne' : ['cc3'], 'cc3.icmp.z' : ['cc3'], 'cc3.icmp.nz' : ['cc3'],
        'addx': ['cc3']
    }
    stack_pointer = 'sp'
    link_reg = 'lr'
    intrinsics = {
        '__byteswaph': IntrinsicInfo([IntrinsicInput(Type.int(2, False), 'input')], [Type.int(4, False)]),
        '__byteswapw': IntrinsicInfo([IntrinsicInput(Type.int(4, False), 'input')], [Type.int(4, False)]),
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
                    *cval_tokens(plus=True, zero=False, signed=True),
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
                    *cval_tokens(plus=True, zero=False, signed=True),
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
                    *cval_tokens(plus=False, zero=True, signed=True),
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
                    case QuarkIntegerOpcode.xchg | QuarkIntegerOpcode.sxb | QuarkIntegerOpcode.sxh | QuarkIntegerOpcode.swaph | QuarkIntegerOpcode.swapw | QuarkIntegerOpcode.neg | QuarkIntegerOpcode.zxb | QuarkIntegerOpcode.zxh:
                        tokens.extend([
                            InstructionTextToken(InstructionTextTokenType.InstructionToken, int_op.name),
                            InstructionTextToken(InstructionTextTokenType.TextToken, " "),
                            InstructionTextToken(InstructionTextTokenType.RegisterToken, reg_name(info.a)),
                            InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ", "),
                            InstructionTextToken(InstructionTextTokenType.RegisterToken, reg_name(info.c)),
                        ])
                    case QuarkIntegerOpcode.not_:
                        tokens.extend([
                            InstructionTextToken(InstructionTextTokenType.InstructionToken, "not"),
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
                    case QuarkIntegerOpcode.bp:
                        tokens.extend([
                            InstructionTextToken(InstructionTextTokenType.InstructionToken, int_op.name),
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
            before = LowLevelILLabel()
            after = LowLevelILLabel()
            if info.cond & 1:
                il.append(
                    il.if_expr(
                        il.flag_group(f"cc{(info.cond >> 1) & 3}"),
                        before,
                        after
                    )
                )
            else:
                il.append(
                    il.if_expr(
                        il.not_expr(0, il.flag_group(f"cc{(info.cond >> 1) & 3}")),
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
                il.append(il.set_reg(4, ra(), il.or_expr(4, il.zero_extend(4, il.low_part(2, ra_expr())), il.const(4, info.immhi))))
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
                il.append(il.jump(il.const(4, addr + 4 + i32(info.imm22 << 2))))
            case QuarkOpcode.call:
                il.append(il.call(il.const(4, addr + 4 + i32(info.imm22 << 2))))
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
                        if info.a == self.ip_reg_index:
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
                    case QuarkIntegerOpcode.bp:
                        il.append(il.breakpoint())
                    case _:
                        il.append(il.unimplemented())
            case QuarkOpcode.cmp:
                cmp_op = QuarkCompareOpcode(info.b & 7)
                match cmp_op:
                    case QuarkCompareOpcode.lt:
                        il.append(il.sub(4, ra_expr(), cval(), flags=f"cc{info.b >> 3}.cmp.lt"))
                    case QuarkCompareOpcode.le:
                        il.append(il.sub(4, ra_expr(), cval(), flags=f"cc{info.b >> 3}.cmp.le"))
                    case QuarkCompareOpcode.ge:
                        il.append(il.sub(4, ra_expr(), cval(), flags=f"cc{info.b >> 3}.cmp.ge"))
                    case QuarkCompareOpcode.gt:
                        il.append(il.sub(4, ra_expr(), cval(), flags=f"cc{info.b >> 3}.cmp.gt"))
                    case QuarkCompareOpcode.eq:
                        il.append(il.sub(4, ra_expr(), cval(), flags=f"cc{info.b >> 3}.cmp.eq"))
                    case QuarkCompareOpcode.ne:
                        il.append(il.sub(4, ra_expr(), cval(), flags=f"cc{info.b >> 3}.cmp.ne"))
                    case QuarkCompareOpcode.nz:
                        il.append(il.and_expr(4, ra_expr(), cval(), flags=f"cc{info.b >> 3}.cmp.nz"))
                    case QuarkCompareOpcode.z:
                        il.append(il.and_expr(4, ra_expr(), cval(), flags=f"cc{info.b >> 3}.cmp.z"))
                    case _:
                        il.append(il.unimplemented())
            case QuarkOpcode.icmp:
                cmp_op = QuarkCompareOpcode(info.b & 7)
                match cmp_op:
                    case QuarkCompareOpcode.lt:
                        il.append(il.sub(4, ra_expr(), cval(), flags=f"cc{info.b >> 3}.icmp.lt"))
                    case QuarkCompareOpcode.le:
                        il.append(il.sub(4, ra_expr(), cval(), flags=f"cc{info.b >> 3}.icmp.le"))
                    case QuarkCompareOpcode.ge:
                        il.append(il.sub(4, ra_expr(), cval(), flags=f"cc{info.b >> 3}.icmp.ge"))
                    case QuarkCompareOpcode.gt:
                        il.append(il.sub(4, ra_expr(), cval(), flags=f"cc{info.b >> 3}.icmp.gt"))
                    case QuarkCompareOpcode.eq:
                        il.append(il.sub(4, ra_expr(), cval(), flags=f"cc{info.b >> 3}.icmp.eq"))
                    case QuarkCompareOpcode.ne:
                        il.append(il.sub(4, ra_expr(), cval(), flags=f"cc{info.b >> 3}.icmp.ne"))
                    case QuarkCompareOpcode.nz:
                        il.append(il.and_expr(4, ra_expr(), cval(), flags=f"cc{info.b >> 3}.icmp.nz"))
                    case QuarkCompareOpcode.z:
                        il.append(il.and_expr(4, ra_expr(), cval(), flags=f"cc{info.b >> 3}.icmp.z"))
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

        def get_expr_for_register_or_constant(size, operand):
            if isinstance(operand, ILRegister):
                return il.reg(size, operand)
            elif isinstance(operand, ILFlag):  # Fixed in >= 5.3
                return il.flag(operand.index)
            elif isinstance(operand, int):
                return il.const(size, operand)
            else:
                assert False, "Not handled"

        def get_expr_for_flag_or_constant(operand):
            # For ADC/SBB/RLC/RRC, the carry flag is passed as a temporary "register"
            # This is super specific and only affects those four instructions and one operand
            if isinstance(operand, ILRegister):
                return il.flag(operand.index)
            elif isinstance(operand, ILFlag):  # Fixed in >= 5.3
                return il.flag(operand.index)
            elif isinstance(operand, int):
                return il.const(size, operand)
            else:
                assert False, "Not handled"

        match write_type:
            case 'cc0.cmp.nz' | 'cc0.icmp.nz' | \
                 'cc1.cmp.nz' | 'cc1.icmp.nz' | \
                 'cc2.cmp.nz' | 'cc2.icmp.nz' | \
                 'cc3.cmp.nz' | 'cc3.icmp.nz':
                return il.compare_not_equal(
                    4,
                    il.and_expr(
                        4,
                        get_expr_for_register_or_constant(4, operands[0]),
                        get_expr_for_register_or_constant(4, operands[1])
                    ),
                    il.const(4, 0)
                )
            case 'cc0.cmp.z' | 'cc0.icmp.z' | \
                 'cc1.cmp.z' | 'cc1.icmp.z' | \
                 'cc2.cmp.z' | 'cc2.icmp.z' | \
                 'cc3.cmp.z' | 'cc3.icmp.z':
                return il.compare_equal(
                    4,
                    il.and_expr(
                        4,
                        get_expr_for_register_or_constant(4, operands[0]),
                        get_expr_for_register_or_constant(4, operands[1])
                    ),
                    il.const(4, 0)
                )
            case '3':
                if op == LowLevelILOperation.LLIL_ADC:
                    # ((first + second + carry) >> 32) & 1
                    return il.compare_unsigned_greater_equal(
                        8,
                        il.add(
                            8,
                            il.zero_extend(8, get_expr_for_register_or_constant(size, operands[0])),
                            il.add(
                                8,
                                il.zero_extend(8, get_expr_for_register_or_constant(size, operands[1])),
                                il.zero_extend(8, get_expr_for_flag_or_constant(operands[2]))
                            )
                        ),
                        il.const(8, 0x1_0000_0000)
                    )
                if op == LowLevelILOperation.LLIL_SBB:
                    # ((first - (second + carry)) >> 32) & 1
                    # Which is always zero unless (second + carry) > first
                    return il.compare_unsigned_greater_than(
                        size,
                        il.add(
                            size,
                            get_expr_for_register_or_constant(size, operands[1]),
                            get_expr_for_flag_or_constant(operands[2])
                        ),
                        get_expr_for_register_or_constant(size, operands[0])
                    )

        return il.unimplemented()

    def get_semantic_flag_group_low_level_il(
        self, sem_group: Optional[SemanticGroupType], il: 'lowlevelil.LowLevelILFunction'
    ) -> 'lowlevelil.ExpressionIndex':
        match sem_group:
            case 'cc0':
                return il.flag('cc0')
            case 'cc1':
                return il.flag('cc1')
            case 'cc2':
                return il.flag('cc2')
            case 'cc3':
                return il.flag('cc3')
            case _:
                return il.unimplemented()

    def convert_to_nop(self, data: bytes, addr: int = 0) -> Optional[bytes]:
        return b'\x00\x00\xc0\x17' * (len(data) // 4)

    def is_never_branch_patch_available(self, data: bytes, addr: int = 0) -> bool:
        return False

    def is_always_branch_patch_available(self, data: bytes, addr: int = 0) -> bool:
        return False

    def is_invert_branch_patch_available(self, data: bytes, addr: int = 0) -> bool:
        return False

    def is_skip_and_return_zero_patch_available(self, data: bytes, addr: int = 0) -> bool:
        return False

    def is_skip_and_return_value_patch_available(self, data: bytes, addr: int = 0) -> bool:
        return False

    def can_assemble(self) -> bool:
        return True

    def assemble(self, code: str, addr: int = 0) -> bytes:
        if isinstance(code, bytes):  # Fixed in >= 5.3
            code = code.decode("utf-8")
        result = b""
        for i, line in enumerate(code.splitlines()):
            if '#' in line:
                line = line[:line.index('#')]
            # tokenize
            tokens = ['']
            for ch in line:
                if ch.isspace():
                    if len(tokens[-1]) > 0:
                        tokens.append('')
                    continue
                if not ch.isalnum() and not ch in "_":
                    if len(tokens[-1]) > 0:
                        tokens.append('')
                tokens[-1] += ch
                if not ch.isalnum() and not ch in "_":
                    if len(tokens[-1]) > 0:
                        tokens.append('')
            if tokens[-1] == '':
                tokens.pop()

            def to_int(x):
                try:
                    return int(x, 0) if x.startswith('0x') else int(x)
                except:
                    return None

            def to_reg(r):
                match r:
                    case "sp":
                        return 0
                    case "lr":
                        return 30
                    case "ip":
                        return 31
                    case reg if reg.startswith("r"):
                        return int(reg[1:])
                    case _:
                        return None

            def to_flag(f):
                match f:
                    case "cc0":
                        return 0
                    case "cc1":
                        return 1
                    case "cc2":
                        return 2
                    case "cc3":
                        return 3
                    case _:
                        return None

            def to_cval(rest):
                #   0
                # + 1
                # - 1
                #   r0
                # + r0
                #   r0 + 1
                # + r0 + 1
                #   r0 - 1
                # + r0 - 1
                #   r0 * 4
                # + r0 * 4
                #   r0 * 4 + 1
                # + r0 * 4 + 1
                #   r0 * 4 - 1
                # + r0 * 4 - 1

                match rest:
                    case [x] if (i := to_int(x)) is not None:
                        return (None, i, None)
                    case ["+", x] if (i := to_int(x)) is not None:
                        return (None, i, None)
                    case ["-", x] if (i := to_int(x)) is not None:
                        return (None, -i, None)
                    case [r] if (reg := to_reg(r)) is not None:
                        return (reg, None, None)
                    case ["+", r] if (reg := to_reg(r)) is not None:
                        return (reg, None, None)
                    case [r, '+', x] if (reg := to_reg(r)) is not None and (i := to_int(x)) is not None:
                        return (reg, i, None)
                    case ["+", r, '+', x] if (reg := to_reg(r)) is not None and (i := to_int(x)) is not None:
                        return (reg, i, None)
                    case [r, '-', x] if (reg := to_reg(r)) is not None and (i := to_int(x)) is not None:
                        return (reg, -i, None)
                    case ["+", r, '-', x] if (reg := to_reg(r)) is not None and (i := to_int(x)) is not None:
                        return (reg, -i, None)
                    case [r, '*', x] if (reg := to_reg(r)) is not None and (i := to_int(x)) is not None:
                        return (reg, None, i)
                    case ["+", r, '*', x] if (reg := to_reg(r)) is not None and (i := to_int(x)) is not None:
                        return (reg, None, i)
                    case [r, '*', x, '+', y] if (reg := to_reg(r)) is not None and (i := to_int(x)) is not None and (i := to_int(y)) is not None:
                        return (reg, int(y, 0), i)
                    case ["+", r, '*', x, '+', y] if (reg := to_reg(r)) is not None and (i := to_int(x)) is not None and (i := to_int(y)) is not None:
                        return (reg, int(y, 0), i)
                    case [r, '*', x, '-', y] if (reg := to_reg(r)) is not None and (i := to_int(x)) is not None and (i := to_int(y)) is not None:
                        return (reg, -int(y, 0), i)
                    case ["+", r, '*', x, '-', y] if (reg := to_reg(r)) is not None and (i := to_int(x)) is not None and (i := to_int(y)) is not None:
                        return (reg, -int(y, 0), i)
                    case _:
                        return (None, None, None)

            def assign_cval(i: QuarkInstruction, cval: Tuple[Optional[int], Optional[int], Optional[int]]):
                if cval[0] is None:
                    if cval[1] is None:
                        # [ ] case
                        i.smallimm = False
                        i.largeimm = True
                        i.imm11 = 0
                        return
                    # [ + const ] case
                    # not sure why we would ever use the imm5 case
                    i.smallimm = False
                    i.largeimm = True
                    i.imm11 = cval[1]
                else:
                    # [ + r ] case
                    i.largeimm = False
                    i.smallimm = False
                    i.c = cval[0]
                    if cval[2] is None:
                        i.d = 0
                    else:
                        # [ + r * mult ] case
                        i.d = math.floor(math.log2(cval[2]))

            i = QuarkInstruction(0)
            match tokens:
                case ["skip", *_]:
                    i.cond = 1
                    tokens.pop(0)
                case ["if", flag, *_] if (flag := to_flag(flag)) is not None:
                    i.cond = 8 | 1 | (flag << 1)
                    tokens.pop(0)
                    tokens.pop(0)
                case ["if", "!", flag, *_] if (flag := to_flag(flag)) is not None:
                    i.cond = 8 | (flag << 1)
                    tokens.pop(0)
                    tokens.pop(0)
                    tokens.pop(0)

            match tokens:
                case [insn, ra, ",", "[", rb, *rest, "]"] if \
                        insn in ["ldb", "ldh", "ldw", "ldbu", "ldhu", "ldwu", "ldsxb", "ldsxh", "ldsxbu", "ldsxhu"] \
                        and (ra := to_reg(ra)) is not None \
                        and (rb := to_reg(rb)) is not None \
                        and (cval := to_cval(rest)) is not None:
                    match insn:
                        case "ldb": i.op = QuarkOpcode.ldb
                        case "ldh": i.op = QuarkOpcode.ldh
                        case "ldw": i.op = QuarkOpcode.ldw
                        case "ldbu": i.op = QuarkOpcode.ldbu
                        case "ldhu": i.op = QuarkOpcode.ldhu
                        case "ldwu": i.op = QuarkOpcode.ldwu
                        case "ldsxb": i.op = QuarkOpcode.ldsxb
                        case "ldsxh": i.op = QuarkOpcode.ldsxh
                        case "ldsxbu": i.op = QuarkOpcode.ldsxbu
                        case "ldsxhu": i.op = QuarkOpcode.ldsxhu
                    i.a = ra
                    i.b = rb
                    assign_cval(i, cval)
                case [insn, ra, ".", ".", "lr", ",", "[", rb, *rest, "]"] if \
                        insn in ["ldmw", "ldmwu"] \
                        and (ra := to_reg(ra)) is not None \
                        and (rb := to_reg(rb)) is not None \
                        and (cval := to_cval(rest)) is not None:
                    match insn:
                        case "ldmw": i.op = QuarkOpcode.ldmw
                        case "ldmwu": i.op = QuarkOpcode.ldmwu
                    i.a = ra
                    i.b = rb
                    assign_cval(i, cval)
                case ["ldi", ra, ",", imm] if \
                        (ra := to_reg(ra)) is not None \
                        and (imm := to_int(imm)) is not None:
                    i.op = QuarkOpcode.ldi
                    i.a = ra
                    i.imm17 = imm
                case ["ldih", ra, ",", imm] if \
                        (ra := to_reg(ra)) is not None \
                        and (imm := to_int(imm)) is not None:
                    i.op = QuarkOpcode.ldih
                    i.a = ra
                    i.immhi = imm
                case [insn, "[", rb, *rest, "]", ",", ra] if \
                        insn in ["stb", "sth", "stw", "stbu", "sthu", "stwu"] \
                        and (ra := to_reg(ra)) is not None \
                        and (rb := to_reg(rb)) is not None \
                        and (cval := to_cval(rest)) is not None:
                    match insn:
                        case "stb": i.op = QuarkOpcode.stb
                        case "sth": i.op = QuarkOpcode.sth
                        case "stw": i.op = QuarkOpcode.stw
                        case "stbu": i.op = QuarkOpcode.stbu
                        case "sthu": i.op = QuarkOpcode.sthu
                        case "stwu": i.op = QuarkOpcode.stwu
                    i.a = ra
                    i.b = rb
                    assign_cval(i, cval)
                case [insn, "[", rb, *rest, "]", ",", ra, ".", ".", "lr"] if \
                        insn in ["stmw", "stmwu"] \
                        and (ra := to_reg(ra)) is not None \
                        and (rb := to_reg(rb)) is not None \
                        and (cval := to_cval(rest)) is not None:
                    match insn:
                        case "stmw": i.op = QuarkOpcode.stmw
                        case "stmwu": i.op = QuarkOpcode.stmwu
                    i.a = ra
                    i.b = rb
                    assign_cval(i, cval)
                case [insn, dest] if \
                        insn in ["jmp", "call"] \
                        and (dest := to_int(dest)) is not None:
                    match insn:
                        case "jmp": i.op = QuarkOpcode.jmp
                        case "call": i.op = QuarkOpcode.call
                    i.imm22 = (dest - addr - 4) >> 2
                case [insn, ra, ",", rb, ",", *rest] if \
                    insn in ["add", "sub", "mul", "div", "idiv", "mod", "imod", "xor", "sar", "shl", "shr", "rol", "ror", "and", "or"] \
                    and (ra := to_reg(ra)) is not None \
                    and (rb := to_reg(rb)) is not None \
                    and (cval := to_cval(rest)) is not None:
                    match insn:
                        case "add": i.op = QuarkOpcode.add
                        case "sub": i.op = QuarkOpcode.sub
                        case "mul": i.op = QuarkOpcode.mul
                        case "div": i.op = QuarkOpcode.div
                        case "idiv": i.op = QuarkOpcode.idiv
                        case "mod": i.op = QuarkOpcode.mod
                        case "imod": i.op = QuarkOpcode.imod
                        case "xor": i.op = QuarkOpcode.xor
                        case "sar": i.op = QuarkOpcode.sar
                        case "shl": i.op = QuarkOpcode.shl
                        case "shr": i.op = QuarkOpcode.shr
                        case "rol": i.op = QuarkOpcode.rol
                        case "ror": i.op = QuarkOpcode.ror
                        case "and": i.op = QuarkOpcode.and_
                        case "or": i.op = QuarkOpcode.or_
                    i.a = ra
                    i.b = rb
                    assign_cval(i, cval)
                case [insn, ra, ",", rb, ",", *rest, ",", "cc3"] if \
                        insn in ["addx", "subx"] \
                        and (ra := to_reg(ra)) is not None \
                        and (rb := to_reg(rb)) is not None \
                        and (cval := to_cval(rest)) is not None:
                    match insn:
                        case "addx": i.op = QuarkOpcode.addx
                        case "subx": i.op = QuarkOpcode.subx
                    i.a = ra
                    i.b = rb
                    assign_cval(i, cval)
                case [insn, rd, ":", ra, ",", rb, ",", rc] if \
                        insn in ["mulx", "imulx"] \
                        and (ra := to_reg(ra)) is not None \
                        and (rb := to_reg(rb)) is not None \
                        and (rc := to_reg(rc)) is not None \
                        and (rd := to_reg(rd)) is not None:
                    match insn:
                        case "mulx": i.op = QuarkOpcode.mulx
                        case "imulx": i.op = QuarkOpcode.imulx
                    i.a = ra
                    i.b = rb
                    i.c = rc
                    i.d = rd
                case ["syscall", num] if \
                        (num := to_int(num)) is not None:
                    i.op = QuarkOpcode.syscall
                    i.imm22 = num
                case ["mov", ra, ",", *rest] if \
                        (ra := to_reg(ra)) is not None \
                        and (cval := to_cval(rest)) is not None:
                    i.op = QuarkOpcode.integer_group
                    i.b = QuarkIntegerOpcode.mov
                    i.a = ra
                    assign_cval(i, cval)
                case [insn, ra, ",", rc] if \
                        insn in ["xchg", "sxb", "sxh", "swaph", "swapw", "neg", "not", "zxb", "zxh"] \
                        and (ra := to_reg(ra)) is not None \
                        and (rc := to_reg(rc)) is not None:
                    i.op = QuarkOpcode.integer_group
                    match insn:
                        case "xchg": i.b = QuarkIntegerOpcode.xchg
                        case "sxb": i.b = QuarkIntegerOpcode.sxb
                        case "sxh": i.b = QuarkIntegerOpcode.sxh
                        case "swaph": i.b = QuarkIntegerOpcode.swaph
                        case "swapw": i.b = QuarkIntegerOpcode.swapw
                        case "neg": i.b = QuarkIntegerOpcode.neg
                        case "not": i.b = QuarkIntegerOpcode.not_
                        case "zxb": i.b = QuarkIntegerOpcode.zxb
                        case "zxh": i.b = QuarkIntegerOpcode.zxh
                    i.a = ra
                    i.c = rc
                case [insn, ra] if \
                        insn in ["call", "syscall", "ldcr", "stcr"] \
                        and (ra := to_reg(ra)) is not None:
                    i.op = QuarkOpcode.integer_group
                    match insn:
                        case "call": i.b = QuarkIntegerOpcode.call
                        case "syscall": i.b = QuarkIntegerOpcode.syscall
                        case "ldcr": i.b = QuarkIntegerOpcode.ldcr
                        case "stcr": i.b = QuarkIntegerOpcode.stcr
                    i.a = ra
                case [insn, fa] if \
                        insn in ["setcc", "clrcc"] \
                        and (fa := to_flag(fa)) is not None:
                    i.op = QuarkOpcode.integer_group
                    match insn:
                        case "setcc": i.b = QuarkIntegerOpcode.setcc
                        case "clrcc": i.b = QuarkIntegerOpcode.clrcc
                    i.a = fa
                case [insn, fa, ",", fc] if \
                        insn in ["notcc", "movcc"] \
                        and (fa := to_flag(fa)) is not None \
                        and (fc := to_flag(fc)) is not None:
                    i.op = QuarkOpcode.integer_group
                    match insn:
                        case "notcc": i.b = QuarkIntegerOpcode.notcc
                        case "movcc": i.b = QuarkIntegerOpcode.movcc
                    i.a = fa
                    i.c = fc
                case [insn, fa, ",", fc, ",", fd] if \
                        insn in ["andcc", "orcc", "xorcc"] \
                        and (fa := to_flag(fa)) is not None \
                        and (fc := to_flag(fc)) is not None \
                        and (fd := to_flag(fd)) is not None:
                    i.op = QuarkOpcode.integer_group
                    match insn:
                        case "andcc": i.b = QuarkIntegerOpcode.andcc
                        case "orcc": i.b = QuarkIntegerOpcode.orcc
                        case "xorcc": i.b = QuarkIntegerOpcode.xorcc
                    i.a = fa
                    i.c = fc
                    i.d = fd
                case ["bp"]:
                    i.op = QuarkOpcode.integer_group
                    i.b = QuarkIntegerOpcode.bp
                case [insn, ".", op, ".", fb, ra, ",", *rest] if \
                        insn in ["cmp", "icmp"] \
                        and op in ["lt", "le", "ge", "gt", "eq", "ne", "z", "nz"] \
                        and (fb := to_flag(fb)) is not None \
                        and (ra := to_reg(ra)) is not None \
                        and (cval := to_cval(rest)) is not None:
                    match insn:
                        case "cmp": i.op = QuarkOpcode.cmp
                        case "icmp": i.op = QuarkOpcode.icmp
                    match op:
                        case "lt": i.b = QuarkCompareOpcode.lt
                        case "le": i.b = QuarkCompareOpcode.le
                        case "ge": i.b = QuarkCompareOpcode.ge
                        case "gt": i.b = QuarkCompareOpcode.gt
                        case "eq": i.b = QuarkCompareOpcode.eq
                        case "ne": i.b = QuarkCompareOpcode.ne
                        case "z": i.b = QuarkCompareOpcode.z
                        case "nz": i.b = QuarkCompareOpcode.nz
                    i.b = i.b | (fb << 3)
                    i.a = ra
                    assign_cval(i, cval)
                case _:
                    raise NotImplemented()
            result += i.instr.to_bytes(4, "little")
            addr += 4
        return result


class QuarkCallingConvention(CallingConvention):
    name = "qcall"
    caller_saved_regs = ['r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9', 'r10', 'r11', 'r12', 'r13', 'r14', 'r15']
    callee_saved_regs = ['r16', 'r17', 'r18', 'r19', 'r20', 'r21', 'r22', 'r23', 'r24', 'r25', 'r26', 'r27', 'r28']
    int_arg_regs = ['r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8']
    int_return_reg = 'r1'
    high_int_return_reg = 'r2'
    arg_regs_for_varargs = False


class QuarkSyscallCallingConvention(CallingConvention):
    name = "qsyscall"
    caller_saved_regs = ['r1', 'r2']
    callee_saved_regs = ['r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9', 'r10', 'r11', 'r12', 'r13', 'r14', 'r15', 'r16', 'r17', 'r18', 'r19', 'r20', 'r21', 'r22', 'r23', 'r24', 'r25', 'r26', 'r27', 'r28']
    int_arg_regs = ['syscall_num', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8']
    int_return_reg = 'r1'
    high_int_return_reg = 'r2'
    eligible_for_heuristics = False


class LinuxQuarkPlatform(Platform):
    name = "linux-quark"
    type_file_path = str(Path(__file__).parent / "types" / "linux-quark.c")

    def view_init(self, view: BinaryView):
        if not isinstance(view, BinaryView):  # Fixed in >= 5.3
            view = BinaryView(handle=binaryninja.core.BNNewViewReference(view))
        WarpContainer['User'].add_source(str(Path(__file__).parent / "signatures" / "quark_stdlib.warp"))
        view.add_type_library(TypeLibrary.from_name(self.arch, "stdlib"))


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

for file in (Path(__file__).parent / "typelib").glob("*.bntl"):
    TypeLibrary.load_from_file(str(file))


def rewrite_lil_relative_load(context: AnalysisContext):
    # rA = const
    # rB = (addr + 4) + rA
    # rA = rB
    # ----------------------
    # rA = (addr + 4 + const)
    # rB = (addr + 4 + const)

    any_replaced = False
    old_llil = context.lifted_il
    new_llil = LowLevelILFunction(old_llil.arch, source_func=old_llil.source_function)
    new_llil.prepare_to_copy_function(old_llil)
    for old_block in old_llil.basic_blocks:
        new_llil.prepare_to_copy_block(old_block)
        instructions = iter(range(old_block.start, old_block.end))
        for old_instr_index in instructions:
            old_instr: LowLevelILInstruction = old_llil[InstructionIndex(old_instr_index)]
            new_llil.set_current_address(old_instr.address, old_block.arch)

            if old_instr_index + 2 < old_block.end:
                next_instr: LowLevelILInstruction = old_llil[InstructionIndex(old_instr_index + 1)]
                next_instr_2: LowLevelILInstruction = old_llil[InstructionIndex(old_instr_index + 2)]
                match (old_instr, next_instr, next_instr_2):
                    case (
                        LowLevelILSetReg(dest=regA, src=LowLevelILConst(constant=const)),
                        LowLevelILSetReg(
                            dest=regB,
                            src=LowLevelILAdd(
                                left=LowLevelILConst(constant=const_2),
                                right=LowLevelILReg(src=regA_2)
                            )
                        ),
                        LowLevelILSetReg(dest=regA_3, src=LowLevelILReg(src=regB_2))
                    ) if const_2 == next_instr_2.address and regA == regA_2 == regA_3 and regB == regB_2:
                        new_llil.append(
                            new_llil.set_reg(
                                old_instr.size,
                                regA,
                                new_llil.const(
                                    old_instr.size,
                                    const + const_2,
                                    loc=next_instr_2.source_location
                                ),
                                loc=old_instr.source_location
                            )
                        )
                        new_llil.append(
                            new_llil.set_reg(
                                old_instr.size,
                                regB,
                                new_llil.const(
                                    old_instr.size,
                                    const + const_2,
                                    loc=next_instr_2.source_location
                                ),
                                loc=next_instr.source_location
                            )
                        )
                        new_llil.append(new_llil.nop(loc=next_instr_2.source_location))
                        next(instructions)
                        next(instructions)
                        any_replaced = True
                        continue

            new_llil.append(old_instr.copy_to(new_llil))

    if any_replaced:
        new_llil.finalize()
        context.lifted_il = new_llil


qwf = Workflow("core.function.metaAnalysis").clone("core.function.metaAnalysis")
qwf.register_activity(Activity(
    configuration=json.dumps({
        "name": "arch.quark.rewrite_relative_load",
        "title": "Quark: Combine Relative Load Instructions",
        "description": "Combine the instructions for relative loads into one instruction, for improvements in signature generation",
        "eligibility": {
            "predicates": [
                {
                    "type": "platform",
                    "operator": "==",
                    "value": "linux-quark",
                }
            ]
        }
    }),
    action=lambda context: rewrite_lil_relative_load(context)
))

qwf.insert_after("core.function.generateLiftedIL", [
    "arch.quark.rewrite_relative_load"
])
qwf.register()

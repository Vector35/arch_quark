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

"""
Example Architecture for the Quark[1] VM architecture

Demonstrating plugin support for:
* Disassembly
* Control Flow
* Patching
* Assembly
* Lifting
* Semantic Flags
* Calling Conventions
* Platform Types
* Type Libraries
* WARP Signatures

Described in detail in our three-part blog series:
1. https://binary.ninja/2026/02/20/quark-platform-part-1.html
2. https://binary.ninja/2026/02/26/quark-platform-part-2.html
3. https://binary.ninja/2026/03/04/quark-platform-part-3.html
"""


# ----------------------------------------------------------------------------------------
# Helper Functions

def rol(i, n):
    """
    Rotate i32 left
    :param i: Integer to rotate
    :param n: Number of bits to rotate
    :return: Rotated value
    """
    return ((i << n) & 0xffffffff) | (i >> (32 - n))


def ror(i, n):
    """
    Rotate i32 right
    :param i: Integer to rotate
    :param n: Number of bits to rotate
    :return: Rotated value
    """
    return (i >> n) | ((i << (32 - n)) & 0xffffffff)


def i32(i):
    """
    Convert u32 to i32 via 2's complement
    :param i: Integer to convert
    :return: `i` but if it was > 0x80000000 then negative and 2's complement
    """
    if i >= 0x80000000:
        return -(0x100000000 - (i & 0xffffffff))
    return i & 0x7fffffff

# ----------------------------------------------------------------------------------------
# Opcodes


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
    integer_group = 0x1f  # See QuarkIntegerOpcode below
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

    cmp = 0x2d  # See QuarkCompareOpcode below
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

# ----------------------------------------------------------------------------------------
# Instruction format and decoding/encoding


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

# ----------------------------------------------------------------------------------------
# Architecture


class QuarkArch(Architecture):
    name = "Quark"
    endianness = Endianness.LittleEndian
    address_size = 4
    default_int_size = 4
    instr_alignment = 1  # Indirect calls can be unaligned
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
        # No ip register. It's handled special
        'syscall_num': RegisterInfo('syscall_num', 4),
    }
    flags = [
        'cc0', 'cc1', 'cc2', 'cc3',
    ]
    flag_roles = {
        # All flags are special, since none are reserved for specific behaviors
        'cc0': FlagRole.SpecialFlagRole,
        'cc1': FlagRole.SpecialFlagRole,
        'cc2': FlagRole.SpecialFlagRole,
        'cc3': FlagRole.SpecialFlagRole,
    }
    semantic_flag_classes = [
        'cmp.lt',  'cmp.le',  'cmp.ge',  'cmp.gt',
        'icmp.lt', 'icmp.le', 'icmp.ge', 'icmp.gt',
        'eq', 'ne', 'z', 'nz',
    ]
    semantic_flag_groups = [
        # Flags are only ever read one at a time
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
            'cmp.lt': LowLevelILFlagCondition.LLFC_ULT,
            'cmp.le': LowLevelILFlagCondition.LLFC_ULE,
            'cmp.ge': LowLevelILFlagCondition.LLFC_UGE,
            'cmp.gt': LowLevelILFlagCondition.LLFC_UGT,
            'icmp.lt': LowLevelILFlagCondition.LLFC_SLT,
            'icmp.le': LowLevelILFlagCondition.LLFC_SLE,
            'icmp.ge': LowLevelILFlagCondition.LLFC_SGE,
            'icmp.gt': LowLevelILFlagCondition.LLFC_SGT,
            'eq': LowLevelILFlagCondition.LLFC_E,
            'ne': LowLevelILFlagCondition.LLFC_NE,
        },
        'cc1': {
            'cmp.lt': LowLevelILFlagCondition.LLFC_ULT,
            'cmp.le': LowLevelILFlagCondition.LLFC_ULE,
            'cmp.ge': LowLevelILFlagCondition.LLFC_UGE,
            'cmp.gt': LowLevelILFlagCondition.LLFC_UGT,
            'icmp.lt': LowLevelILFlagCondition.LLFC_SLT,
            'icmp.le': LowLevelILFlagCondition.LLFC_SLE,
            'icmp.ge': LowLevelILFlagCondition.LLFC_SGE,
            'icmp.gt': LowLevelILFlagCondition.LLFC_SGT,
            'eq': LowLevelILFlagCondition.LLFC_E,
            'ne': LowLevelILFlagCondition.LLFC_NE,
        },
        'cc2': {
            'cmp.lt': LowLevelILFlagCondition.LLFC_ULT,
            'cmp.le': LowLevelILFlagCondition.LLFC_ULE,
            'cmp.ge': LowLevelILFlagCondition.LLFC_UGE,
            'cmp.gt': LowLevelILFlagCondition.LLFC_UGT,
            'icmp.lt': LowLevelILFlagCondition.LLFC_SLT,
            'icmp.le': LowLevelILFlagCondition.LLFC_SLE,
            'icmp.ge': LowLevelILFlagCondition.LLFC_SGE,
            'icmp.gt': LowLevelILFlagCondition.LLFC_SGT,
            'eq': LowLevelILFlagCondition.LLFC_E,
            'ne': LowLevelILFlagCondition.LLFC_NE,
        },
        'cc3': {
            'cmp.lt': LowLevelILFlagCondition.LLFC_ULT,
            'cmp.le': LowLevelILFlagCondition.LLFC_ULE,
            'cmp.ge': LowLevelILFlagCondition.LLFC_UGE,
            'cmp.gt': LowLevelILFlagCondition.LLFC_UGT,
            'icmp.lt': LowLevelILFlagCondition.LLFC_SLT,
            'icmp.le': LowLevelILFlagCondition.LLFC_SLE,
            'icmp.ge': LowLevelILFlagCondition.LLFC_SGE,
            'icmp.gt': LowLevelILFlagCondition.LLFC_SGT,
            'eq': LowLevelILFlagCondition.LLFC_E,
            'ne': LowLevelILFlagCondition.LLFC_NE,
        },
    }
    semantic_class_for_flag_write_type = {
        'cmp.lt.cc0':  'cmp.lt',  'cmp.le.cc0':  'cmp.le',  'cmp.ge.cc0':  'cmp.ge',  'cmp.gt.cc0':  'cmp.gt',  'cmp.eq.cc0':  'eq', 'cmp.ne.cc0':  'ne', 'cmp.z.cc0':  'z', 'cmp.nz.cc0':  'nz',
        'icmp.lt.cc0': 'icmp.lt', 'icmp.le.cc0': 'icmp.le', 'icmp.ge.cc0': 'icmp.ge', 'icmp.gt.cc0': 'icmp.gt', 'icmp.eq.cc0': 'eq', 'icmp.ne.cc0': 'ne', 'icmp.z.cc0': 'z', 'icmp.nz.cc0': 'nz',
        'cmp.lt.cc1':  'cmp.lt',  'cmp.le.cc1':  'cmp.le',  'cmp.ge.cc1':  'cmp.ge',  'cmp.gt.cc1':  'cmp.gt',  'cmp.eq.cc1':  'eq', 'cmp.ne.cc1':  'ne', 'cmp.z.cc1':  'z', 'cmp.nz.cc1':  'nz',
        'icmp.lt.cc1': 'icmp.lt', 'icmp.le.cc1': 'icmp.le', 'icmp.ge.cc1': 'icmp.ge', 'icmp.gt.cc1': 'icmp.gt', 'icmp.eq.cc1': 'eq', 'icmp.ne.cc1': 'ne', 'icmp.z.cc1': 'z', 'icmp.nz.cc1': 'nz',
        'cmp.lt.cc2':  'cmp.lt',  'cmp.le.cc2':  'cmp.le',  'cmp.ge.cc2':  'cmp.ge',  'cmp.gt.cc2':  'cmp.gt',  'cmp.eq.cc2':  'eq', 'cmp.ne.cc2':  'ne', 'cmp.z.cc2':  'z', 'cmp.nz.cc2':  'nz',
        'icmp.lt.cc2': 'icmp.lt', 'icmp.le.cc2': 'icmp.le', 'icmp.ge.cc2': 'icmp.ge', 'icmp.gt.cc2': 'icmp.gt', 'icmp.eq.cc2': 'eq', 'icmp.ne.cc2': 'ne', 'icmp.z.cc2': 'z', 'icmp.nz.cc2': 'nz',
        'cmp.lt.cc3':  'cmp.lt',  'cmp.le.cc3':  'cmp.le',  'cmp.ge.cc3':  'cmp.ge',  'cmp.gt.cc3':  'cmp.gt',  'cmp.eq.cc3':  'eq', 'cmp.ne.cc3':  'ne', 'cmp.z.cc3':  'z', 'cmp.nz.cc3':  'nz',
        'icmp.lt.cc3': 'icmp.lt', 'icmp.le.cc3': 'icmp.le', 'icmp.ge.cc3': 'icmp.ge', 'icmp.gt.cc3': 'icmp.gt', 'icmp.eq.cc3': 'eq', 'icmp.ne.cc3': 'ne', 'icmp.z.cc3': 'z', 'icmp.nz.cc3': 'nz',
    }
    flag_write_types = {
        # Each of the 8 unsigned comparisons that could affect cc0
        'cmp.lt.cc0',  'cmp.le.cc0',  'cmp.ge.cc0',  'cmp.gt.cc0',  'cmp.eq.cc0',  'cmp.ne.cc0',  'cmp.z.cc0',  'cmp.nz.cc0',
        # Same thing for the signed comparisons
        'icmp.lt.cc0', 'icmp.le.cc0', 'icmp.ge.cc0', 'icmp.gt.cc0', 'icmp.eq.cc0', 'icmp.ne.cc0', 'icmp.z.cc0', 'icmp.nz.cc0',
        # Same thing for the other flags
        'cmp.lt.cc1',  'cmp.le.cc1',  'cmp.ge.cc1',  'cmp.gt.cc1',  'cmp.eq.cc1',  'cmp.ne.cc1',  'cmp.z.cc1',  'cmp.nz.cc1',
        'icmp.lt.cc1', 'icmp.le.cc1', 'icmp.ge.cc1', 'icmp.gt.cc1', 'icmp.eq.cc1', 'icmp.ne.cc1', 'icmp.z.cc1', 'icmp.nz.cc1',
        'cmp.lt.cc2',  'cmp.le.cc2',  'cmp.ge.cc2',  'cmp.gt.cc2',  'cmp.eq.cc2',  'cmp.ne.cc2',  'cmp.z.cc2',  'cmp.nz.cc2',
        'icmp.lt.cc2', 'icmp.le.cc2', 'icmp.ge.cc2', 'icmp.gt.cc2', 'icmp.eq.cc2', 'icmp.ne.cc2', 'icmp.z.cc2', 'icmp.nz.cc2',
        'cmp.lt.cc3',  'cmp.le.cc3',  'cmp.ge.cc3',  'cmp.gt.cc3',  'cmp.eq.cc3',  'cmp.ne.cc3',  'cmp.z.cc3',  'cmp.nz.cc3',
        'icmp.lt.cc3', 'icmp.le.cc3', 'icmp.ge.cc3', 'icmp.gt.cc3', 'icmp.eq.cc3', 'icmp.ne.cc3', 'icmp.z.cc3', 'icmp.nz.cc3',
        # And addx, which has its own special behavior
        'addx'
    }
    flags_written_by_flag_write_type = {
        # Each of these comparisons only affects one flag at a time
        'cmp.lt.cc0':  ['cc0'], 'cmp.le.cc0':  ['cc0'], 'cmp.ge.cc0':  ['cc0'], 'cmp.gt.cc0':  ['cc0'], 'cmp.eq.cc0':  ['cc0'], 'cmp.ne.cc0':  ['cc0'], 'cmp.z.cc0':  ['cc0'], 'cmp.nz.cc0':  ['cc0'],
        'icmp.lt.cc0': ['cc0'], 'icmp.le.cc0': ['cc0'], 'icmp.ge.cc0': ['cc0'], 'icmp.gt.cc0': ['cc0'], 'icmp.eq.cc0': ['cc0'], 'icmp.ne.cc0': ['cc0'], 'icmp.z.cc0': ['cc0'], 'icmp.nz.cc0': ['cc0'],
        'cmp.lt.cc1':  ['cc1'], 'cmp.le.cc1':  ['cc1'], 'cmp.ge.cc1':  ['cc1'], 'cmp.gt.cc1':  ['cc1'], 'cmp.eq.cc1':  ['cc1'], 'cmp.ne.cc1':  ['cc1'], 'cmp.z.cc1':  ['cc1'], 'cmp.nz.cc1':  ['cc1'],
        'icmp.lt.cc1': ['cc1'], 'icmp.le.cc1': ['cc1'], 'icmp.ge.cc1': ['cc1'], 'icmp.gt.cc1': ['cc1'], 'icmp.eq.cc1': ['cc1'], 'icmp.ne.cc1': ['cc1'], 'icmp.z.cc1': ['cc1'], 'icmp.nz.cc1': ['cc1'],
        'cmp.lt.cc2':  ['cc2'], 'cmp.le.cc2':  ['cc2'], 'cmp.ge.cc2':  ['cc2'], 'cmp.gt.cc2':  ['cc2'], 'cmp.eq.cc2':  ['cc2'], 'cmp.ne.cc2':  ['cc2'], 'cmp.z.cc2':  ['cc2'], 'cmp.nz.cc2':  ['cc2'],
        'icmp.lt.cc2': ['cc2'], 'icmp.le.cc2': ['cc2'], 'icmp.ge.cc2': ['cc2'], 'icmp.gt.cc2': ['cc2'], 'icmp.eq.cc2': ['cc2'], 'icmp.ne.cc2': ['cc2'], 'icmp.z.cc2': ['cc2'], 'icmp.nz.cc2': ['cc2'],
        'cmp.lt.cc3':  ['cc3'], 'cmp.le.cc3':  ['cc3'], 'cmp.ge.cc3':  ['cc3'], 'cmp.gt.cc3':  ['cc3'], 'cmp.eq.cc3':  ['cc3'], 'cmp.ne.cc3':  ['cc3'], 'cmp.z.cc3':  ['cc3'], 'cmp.nz.cc3':  ['cc3'],
        'icmp.lt.cc3': ['cc3'], 'icmp.le.cc3': ['cc3'], 'icmp.ge.cc3': ['cc3'], 'icmp.gt.cc3': ['cc3'], 'icmp.eq.cc3': ['cc3'], 'icmp.ne.cc3': ['cc3'], 'icmp.z.cc3': ['cc3'], 'icmp.nz.cc3': ['cc3'],
        # addx always modifies the cc3 flag
        'addx': ['cc3']
    }
    stack_pointer = 'sp'
    link_reg = 'lr'
    intrinsics = {
        '__byteswaph': IntrinsicInfo(
            # Inputs
            [IntrinsicInput(Type.int(2, False), 'input')],
            # Outputs
            [Type.int(4, False)]
        ),
        '__byteswapw': IntrinsicInfo([IntrinsicInput(Type.int(4, False), 'input')], [Type.int(4, False)]),
    }

    ip_reg_index = 31

    # ------------------------------------------------------------------------------------
    # Control Flow

    def get_instruction_info(self, data: bytes, addr: int) -> Optional[InstructionInfo]:
        info = QuarkInstruction(int.from_bytes(data, 'little'))
        try:
            op = QuarkOpcode(info.op)
        except ValueError:
            print(f"Invalid opcode {info.op:#x} at {addr:#x} {data}")
            return None

        result = InstructionInfo()
        result.length = 4

        # Technically, every instruction with a conditional bit *can* jump
        # but only handle the ones that are actually jump instructions here.
        # The others will be figured out when lifting
        match op:
            case QuarkOpcode.jmp:
                if info.cond & 8:
                    if info.cond & 1:  # Jump if condition is met
                        result.add_branch(BranchType.TrueBranch, addr + 4 + i32(info.imm22 << 2))
                        result.add_branch(BranchType.FalseBranch, addr + 4)
                    else:  # Jump if condition is NOT met
                        result.add_branch(BranchType.TrueBranch, addr + 4)
                        result.add_branch(BranchType.FalseBranch, addr + 4 + i32(info.imm22 << 2))
                else:  # Unconditional jump
                    result.add_branch(BranchType.UnconditionalBranch, addr + 4 + i32(info.imm22 << 2))
            case QuarkOpcode.call:  # Call relative
                result.add_branch(BranchType.CallDestination, addr + 4 + i32(info.imm22 << 2))
            case QuarkOpcode.syscall:
                result.add_branch(BranchType.SystemCall)
            case QuarkOpcode.integer_group:
                int_op = QuarkIntegerOpcode(info.b)
                match int_op:
                    case QuarkIntegerOpcode.mov:
                        # Move to ip is a jump
                        # Could have included all other instructions that write to ip
                        if info.a == self.ip_reg_index:
                            result.add_branch(BranchType.IndirectBranch)
                    case QuarkIntegerOpcode.call: # Indirect call
                        result.add_branch(BranchType.CallDestination)
                    case QuarkIntegerOpcode.syscall:
                        result.add_branch(BranchType.SystemCall)

        return result

    # ------------------------------------------------------------------------------------
    # Disassembly

    def get_instruction_text(self, data: bytes, addr: int) -> Optional[Tuple[List['function.InstructionTextToken'], int]]:
        info = QuarkInstruction(int.from_bytes(data, 'little'))
        try:
            op = QuarkOpcode(info.op)
        except ValueError:
            print(f"Invalid opcode {info.op:#x} at {addr:#x} {data}")
            return None

        tokens = []

        # Conditional instructions start with `if ccX`
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
            # Could replace entire instruction with `nop` but this lets us see what was there
            tokens.extend([
                InstructionTextToken(InstructionTextTokenType.TextToken, "skip"),
                InstructionTextToken(InstructionTextTokenType.TextToken, " "),
            ])

        def reg_name(reg):
            """
            Convert register index to name
            :param reg: Register index from instruction
            :return: Register name
            """
            if reg == self.ip_reg_index:
                return "ip"
            return self.get_reg_name(reg)

        def cval_tokens(plus: bool, zero: bool, signed: bool):
            """
            Get tokens for cval addressing mode
            :param plus: If a + should be prepended, to match - being prepended for negative constants
            :param zero: If empty cval should return a token for 0
            :param signed: If integers should decode as signed with 2's complement i32s
            :return: List of tokens to insert into disassembly
            """
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
                # Never seen this used in practice but the interpreter supports it
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
            # Gets its own to handle "and" being a reserved keyword
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
            # Same as and_
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
                    # Gets its own to handle "not" being a reserved keyword
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
                    # cmp.lt.cc0
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

    # ------------------------------------------------------------------------------------
    # Lifting

    def get_instruction_low_level_il(self, data: bytes, addr: int, il: LowLevelILFunction) -> Optional[int]:
        info = QuarkInstruction(int.from_bytes(data, 'little'))
        try:
            op = QuarkOpcode(info.op)
        except ValueError:
            print(f"Invalid opcode {info.op:#x} at {addr:#x} {data}")
            return None

        # Get name of register in `a` component of instruction
        def ra():
            # sanity: make sure we don't lift anything that references ip directly
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

        # Get expression to get the register in `a` component of instruction
        def ra_expr():
            # Special case ip register by emitting a constant with its value
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

        # Addressing modes
        def cval():
            if info.largeimm:
                return il.const(4, info.imm11)
            elif info.smallimm:
                return il.const(4, rol(info.imm5, info.d))
            else:
                if info.d == 0:
                    return rc_expr()
                # Temp is probably overkill here, but maybe it will save us from the x86 problem
                # of foo = *(bar + (baz * 8)) being annoying to pattern match
                il.append(il.set_reg(4, LLIL_TEMP(0), il.shift_left(4, rc_expr(), il.const(4, info.d))))
                return il.reg(4, LLIL_TEMP(0))

        # Since any instruction can write to any register (including IP), we need to handle
        # potentially causing a jump at any point
        # Uses the same signature as il.set_reg for easy find+replace
        def set_reg_or_jmp(size, reg, value):
            if reg == self.ip_reg_index:
                return il.jump(value)
            else:
                return il.set_reg(size, reg, value)

        after = None
        if info.cond & 8:
            # Conditionally executed
            before = LowLevelILLabel()
            after = LowLevelILLabel()
            if info.cond & 1:  # Execute instruction if condition is true
                il.append(
                    il.if_expr(
                        il.flag_group(f"cc{(info.cond >> 1) & 3}"),
                        before,
                        after
                    )
                )
            else:  # Execute instruction if condition is false
                il.append(
                    il.if_expr(
                        il.not_expr(0, il.flag_group(f"cc{(info.cond >> 1) & 3}")),
                        before,
                        after
                    )
                )
            # Label right before the real instruction, jumping here will execute it normally
            il.mark_label(before)
        elif info.cond & 1:
            # Always skipped apparently
            il.append(il.nop())
            return 4

        match op:
            case QuarkOpcode.ldb:  # load byte
                il.append(set_reg_or_jmp(4, info.a, il.zero_extend(4, il.load(1, il.add(4, rb_expr(), cval())))))
            case QuarkOpcode.ldh:  # load halfword
                il.append(set_reg_or_jmp(4, info.a, il.zero_extend(4, il.load(2, il.add(4, rb_expr(), cval())))))
            case QuarkOpcode.ldw:  # load word
                il.append(set_reg_or_jmp(4, info.a, il.load(4, il.add(4, rb_expr(), cval()))))
            case QuarkOpcode.ldbu:  # load byte and increment source
                addr = LLIL_TEMP(1)
                il.append(il.set_reg(4, addr, il.add(4, rb_expr(), cval())))
                il.append(set_reg_or_jmp(4, info.b, il.add(4, il.reg(4, addr), il.const(4, 1))))
                il.append(set_reg_or_jmp(4, info.a, il.zero_extend(4, il.load(1, il.reg(4, addr)))))
            case QuarkOpcode.ldhu:  # load halfword and increment source
                addr = LLIL_TEMP(1)
                il.append(il.set_reg(4, addr, il.add(4, rb_expr(), cval())))
                il.append(set_reg_or_jmp(4, info.b, il.add(4, il.reg(4, addr), il.const(4, 2))))
                il.append(set_reg_or_jmp(4, info.a, il.zero_extend(4, il.load(2, il.reg(4, addr)))))
            case QuarkOpcode.ldwu:  # load word and increment source
                addr = LLIL_TEMP(1)
                il.append(il.set_reg(4, addr, il.add(4, rb_expr(), cval())))
                il.append(set_reg_or_jmp(4, info.b, il.add(4, il.reg(4, addr), il.const(4, 4))))
                il.append(set_reg_or_jmp(4, info.a, il.load(4, il.reg(4, addr))))
            case QuarkOpcode.ldmw:  # load multiple words
                addr = LLIL_TEMP(1)
                # (= addr (+ rb + cval))
                il.append(il.set_reg(4, addr, il.add(4, rb_expr(), cval())))
                for i in range(info.a, 31):
                    # (= temp2 (+ addr [(i-a) * 4])
                    il.append(il.set_reg(4, LLIL_TEMP(2), il.add(4, il.reg(4, addr), il.const(4, (i - info.a) * 4))))
                    # (= (reg i) (load (temp2))
                    il.append(il.set_reg(4, il.arch.get_reg_name(i), il.load(4, il.reg(4, LLIL_TEMP(2)))))
            case QuarkOpcode.ldmwu:  # load multiple words and increment source
                addr = LLIL_TEMP(1)
                # (= addr (+ rb + cval))
                il.append(il.set_reg(4, addr, il.add(4, rb_expr(), cval())))
                # (= rb (+ addr [(31 - a) * 4]))
                il.append(set_reg_or_jmp(4, info.b, il.add(4, il.reg(4, addr), il.const(4, (31 - info.a) * 4))))
                for i in range(info.a, 31):
                    # (= temp2 (+ addr [(i-a) * 4])
                    il.append(il.set_reg(4, LLIL_TEMP(2), il.add(4, il.reg(4, addr), il.const(4, (i - info.a) * 4))))
                    # (= (reg i) (load (temp2))
                    il.append(il.set_reg(4, il.arch.get_reg_name(i), il.load(4, il.reg(4, LLIL_TEMP(2)))))
            case QuarkOpcode.ldsxb:  # load sign extended byte
                il.append(set_reg_or_jmp(4, info.a, il.sign_extend(4, il.load(1, il.add(4, rb_expr(), cval())))))
            case QuarkOpcode.ldsxh:  # load sign extended halfword
                il.append(set_reg_or_jmp(4, info.a, il.sign_extend(4, il.load(2, il.add(4, rb_expr(), cval())))))
            case QuarkOpcode.ldsxbu:  # load sign extended byte and increment source
                addr = LLIL_TEMP(1)
                il.append(il.set_reg(4, addr, il.add(4, rb_expr(), cval())))
                il.append(set_reg_or_jmp(4, info.b, il.add(4, il.reg(4, addr), il.const(4, 1))))
                il.append(set_reg_or_jmp(4, info.a, il.sign_extend(4, il.load(1, il.reg(4, addr)))))
            case QuarkOpcode.ldsxhu:  # load sign extended halfword and increment source
                addr = LLIL_TEMP(1)
                il.append(il.set_reg(4, addr, il.add(4, rb_expr(), cval())))
                il.append(set_reg_or_jmp(4, info.b, il.add(4, il.reg(4, addr), il.const(4, 1))))
                il.append(set_reg_or_jmp(4, info.a, il.sign_extend(4, il.load(2, il.reg(4, addr)))))
            case QuarkOpcode.ldi:  # load immediate
                il.append(set_reg_or_jmp(4, info.a, il.const(4, info.imm17)))
            case QuarkOpcode.ldih:  # load high immediate (16 bits, only place this is used)
                il.append(set_reg_or_jmp(4, info.a, il.or_expr(4, il.zero_extend(4, il.low_part(2, ra_expr())), il.const(4, info.immhi))))
            case QuarkOpcode.stb:  # store byte
                il.append(il.store(1, il.add(4, rb_expr(), cval()), il.low_part(1, ra_expr())))
            case QuarkOpcode.sth:  # store halfword
                il.append(il.store(2, il.add(4, rb_expr(), cval()), il.low_part(2, ra_expr())))
            case QuarkOpcode.stw:  # store word
                il.append(il.store(4, il.add(4, rb_expr(), cval()), ra_expr()))
            case QuarkOpcode.stbu:  # store byte and increment source
                addr = LLIL_TEMP(1)
                il.append(il.set_reg(4, addr, il.add(4, rb_expr(), cval())))
                il.append(set_reg_or_jmp(4, info.b, il.reg(4, addr)))
                il.append(il.store(1, il.reg(4, addr), il.low_part(1, ra_expr())))
            case QuarkOpcode.sthu:  # store halfword and increment source
                addr = LLIL_TEMP(1)
                il.append(il.set_reg(4, addr, il.add(4, rb_expr(), cval())))
                il.append(set_reg_or_jmp(4, info.b, il.reg(4, addr)))
                il.append(il.store(2, il.reg(4, addr), il.low_part(2, ra_expr())))
            case QuarkOpcode.stwu:  # store word and increment source
                addr = LLIL_TEMP(1)
                il.append(il.set_reg(4, addr, il.add(4, rb_expr(), cval())))
                il.append(set_reg_or_jmp(4, info.b, il.reg(4, addr)))
                il.append(il.store(4, il.reg(4, addr), ra_expr()))
            case QuarkOpcode.stmw:  # store multiple words
                addr = LLIL_TEMP(1)
                # (= addr (+ rb + cval))
                il.append(il.set_reg(4, addr, il.add(4, rb_expr(), cval())))
                for i in range(info.a, 31):
                    # (= temp2 (+ addr [(i-a) * 4])
                    il.append(il.set_reg(4, LLIL_TEMP(2), il.add(4, il.reg(4, addr), il.const(4, (i - info.a) * 4))))
                    # (store temp2 (reg i))
                    il.append(il.store(4, il.reg(4, LLIL_TEMP(2)), il.reg(4, il.arch.get_reg_name(i))))
            case QuarkOpcode.stmwu:  # store multiple words and increment source
                addr = LLIL_TEMP(1)
                # (= addr (+ rb + cval))
                il.append(il.set_reg(4, addr, il.add(4, rb_expr(), cval())))
                for i in range(info.a, 31):
                    # (= temp2 (+ addr [(i-a) * 4])
                    il.append(il.set_reg(4, LLIL_TEMP(2), il.add(4, il.reg(4, addr), il.const(4, (i - info.a) * 4))))
                    # (store temp2 (reg i))
                    il.append(il.store(4, il.reg(4, LLIL_TEMP(2)), il.reg(4, il.arch.get_reg_name(i))))
                # (= rb addr)
                il.append(set_reg_or_jmp(4, info.b, il.reg(4, addr)))
            case QuarkOpcode.jmp:  # jump relative
                il.append(il.jump(il.const(4, addr + 4 + i32(info.imm22 << 2))))
            case QuarkOpcode.call:  # direct call relative
                il.append(il.call(il.const(4, addr + 4 + i32(info.imm22 << 2))))
            case QuarkOpcode.add:  # add
                il.append(set_reg_or_jmp(4, info.a, il.add(4, rb_expr(), cval())))
            case QuarkOpcode.sub:  # subtract
                il.append(set_reg_or_jmp(4, info.a, il.sub(4, rb_expr(), cval())))
            case QuarkOpcode.addx:  # add with carry
                il.append(set_reg_or_jmp(4, info.a, il.add_carry(4, rb_expr(), cval(), il.flag('cc3'), flags='addx')))
            case QuarkOpcode.subx:  # subtract with borrow
                il.append(set_reg_or_jmp(4, info.a, il.sub_borrow(4, rb_expr(), cval(), il.flag('cc3'), flags='addx')))
            case QuarkOpcode.mulx:  # double precision multiply
                # The set_reg_split call could have either half output into ip,
                # so output to temporary registers and then set those
                il.append(il.set_reg_split(4, LLIL_TEMP(1), LLIL_TEMP(2), il.mult_double_prec_unsigned(4, rb_expr(), rc_expr())))
                # We need to modify ra first in case ra == rd, but if ra == rd == ip
                # then modifying ra first would cause the jump to happen and skip modifying rd.
                # Since ra == rd clobbers ra anyway, we can skip that write and solve this while
                # keeping the semantics of the instruction correct.
                if info.a != info.d:
                    il.append(set_reg_or_jmp(4, info.a, il.reg(4, LLIL_TEMP(2))))
                il.append(set_reg_or_jmp(4, info.d, il.reg(4, LLIL_TEMP(1))))
            case QuarkOpcode.imulx:  # double precision signed multiply
                il.append(il.set_reg_split(4, LLIL_TEMP(1), LLIL_TEMP(2), il.mult_double_prec_signed(4, rb_expr(), rc_expr())))
                if info.a != info.d:
                    il.append(set_reg_or_jmp(4, info.a, il.reg(4, LLIL_TEMP(2))))
                il.append(set_reg_or_jmp(4, info.d, il.reg(4, LLIL_TEMP(1))))
            case QuarkOpcode.mul:  # single precision multiply
                il.append(set_reg_or_jmp(4, info.a, il.mult(4, rb_expr(), cval())))
            case QuarkOpcode.div:  # unsigned division
                il.append(set_reg_or_jmp(4, info.a, il.div_unsigned(4, rb_expr(), cval())))
            case QuarkOpcode.idiv:  # signed division
                il.append(set_reg_or_jmp(4, info.a, il.div_signed(4, rb_expr(), cval())))
            case QuarkOpcode.mod:  # unsigned modulo
                il.append(set_reg_or_jmp(4, info.a, il.mod_unsigned(4, rb_expr(), cval())))
            case QuarkOpcode.imod:  # signed modulo
                il.append(set_reg_or_jmp(4, info.a, il.mod_signed(4, rb_expr(), cval())))
            case QuarkOpcode.and_:  # bit and
                il.append(set_reg_or_jmp(4, info.a, il.and_expr(4, rb_expr(), cval())))
            case QuarkOpcode.or_:  # bit or
                il.append(set_reg_or_jmp(4, info.a, il.or_expr(4, rb_expr(), cval())))
            case QuarkOpcode.xor:  # bit xor
                il.append(set_reg_or_jmp(4, info.a, il.xor_expr(4, rb_expr(), cval())))
            case QuarkOpcode.sar:  # arithmetic shift right
                il.append(set_reg_or_jmp(4, info.a, il.arith_shift_right(4, rb_expr(), cval())))
            case QuarkOpcode.shl:  # logical shift left (and arithmetic, they're the same)
                il.append(set_reg_or_jmp(4, info.a, il.shift_left(4, rb_expr(), cval())))
            case QuarkOpcode.shr:  # logical shift right
                il.append(set_reg_or_jmp(4, info.a, il.logical_shift_right(4, rb_expr(), cval())))
            case QuarkOpcode.rol:  # rotate left
                il.append(set_reg_or_jmp(4, info.a, il.rotate_left(4, rb_expr(), cval())))
            case QuarkOpcode.ror:  # rotate right
                il.append(set_reg_or_jmp(4, info.a, il.rotate_right(4, rb_expr(), cval())))
            case QuarkOpcode.syscall:  # system call
                il.append(il.set_reg(4, 'syscall_num', il.const(4, info.imm22)))
                il.append(il.system_call())
            case QuarkOpcode.integer_group:
                int_op = QuarkIntegerOpcode(info.b)
                match int_op:
                    case QuarkIntegerOpcode.mov:  # move to register
                        il.append(set_reg_or_jmp(4, info.a, cval()))
                    case QuarkIntegerOpcode.xchg:  # exchange registers
                        result = LLIL_TEMP(1)
                        il.append(il.set_reg(4, result, ra_expr()))
                        il.append(set_reg_or_jmp(4, info.a, rc_expr()))
                        il.append(set_reg_or_jmp(4, info.c, il.reg(4, result)))
                    case QuarkIntegerOpcode.sxb:  # sign extend byte
                        il.append(set_reg_or_jmp(4, info.a, il.sign_extend(4, il.low_part(1, rc_expr()))))
                    case QuarkIntegerOpcode.sxh:  # sign extend halfword
                        il.append(set_reg_or_jmp(4, info.a, il.sign_extend(4, il.low_part(2, rc_expr()))))
                    case QuarkIntegerOpcode.swaph:  # endian byte swap halfword
                        il.append(il.intrinsic([ra()], '__byteswaph', [il.low_part(2, rc_expr())]))
                    case QuarkIntegerOpcode.swapw:  # endian byte swap word
                        il.append(il.intrinsic([ra()], '__byteswapw', [rc_expr()]))
                    case QuarkIntegerOpcode.call:  # indirect call
                        addr = LLIL_TEMP(1)
                        il.append(il.set_reg(4, addr, ra_expr()))
                        il.append(il.call(il.reg(4, addr)))
                    case QuarkIntegerOpcode.neg:  # bit negate
                        il.append(set_reg_or_jmp(4, info.a, il.neg_expr(4, rc_expr())))
                    case QuarkIntegerOpcode.not_:  # bit not
                        il.append(set_reg_or_jmp(4, info.a, il.not_expr(4, rc_expr())))
                    case QuarkIntegerOpcode.zxb:  # zero extend byte
                        il.append(set_reg_or_jmp(4, info.a, il.zero_extend(4, il.low_part(1, rc_expr()))))
                    case QuarkIntegerOpcode.zxh:  # zero extend halfword
                        il.append(set_reg_or_jmp(4, info.a, il.zero_extend(4, il.low_part(2, rc_expr()))))
                    case QuarkIntegerOpcode.ldcr:  # load flags to register
                        cc0 = il.flag_bit(4, 'cc0', 0)
                        cc1 = il.flag_bit(4, 'cc1', 8)
                        cc2 = il.flag_bit(4, 'cc2', 16)
                        cc3 = il.flag_bit(4, 'cc3', 24)
                        il.append(set_reg_or_jmp(4, info.a, il.or_expr(4, cc3, il.or_expr(4, cc2, il.or_expr(4, cc1, cc0)))))
                    case QuarkIntegerOpcode.stcr:  # store register to flags
                        il.append(il.set_reg(1, LLIL_TEMP(0), ra_expr()))
                        il.append(il.set_flag('cc0', il.test_bit(4, il.reg(4, LLIL_TEMP(0)), il.const(4, 0x1))))
                        il.append(il.set_flag('cc1', il.test_bit(4, il.reg(4, LLIL_TEMP(0)), il.const(4, 0x100))))
                        il.append(il.set_flag('cc2', il.test_bit(4, il.reg(4, LLIL_TEMP(0)), il.const(4, 0x10000))))
                        il.append(il.set_flag('cc3', il.test_bit(4, il.reg(4, LLIL_TEMP(0)), il.const(4, 0x1000000))))
                    case QuarkIntegerOpcode.syscall:  # system call by reg
                        il.append(il.set_reg(4, 'syscall_num', ra_expr()))
                        il.append(il.system_call())
                    case QuarkIntegerOpcode.setcc:  # set flag
                        il.append(il.set_flag(il.arch.get_flag_index(f"cc{info.a & 3}"), il.const(0, 1)))
                    case QuarkIntegerOpcode.clrcc:  # clear flag
                        il.append(il.set_flag(il.arch.get_flag_index(f"cc{info.a & 3}"), il.const(0, 0)))
                    case QuarkIntegerOpcode.notcc:  # invert flag
                        il.append(il.set_flag(il.arch.get_flag_index(f"cc{info.a & 3}"), il.not_expr(0, il.flag(f"cc{info.c & 3}"))))
                    case QuarkIntegerOpcode.movcc:  # move flag
                        il.append(il.set_flag(il.arch.get_flag_index(f"cc{info.a & 3}"), il.flag(f"cc{info.c & 3}")))
                    case QuarkIntegerOpcode.andcc:  # and flag
                        il.append(il.set_flag(il.arch.get_flag_index(f"cc{info.a & 3}"), il.and_expr(0, il.flag(f"cc{info.c & 3}"), il.flag(f"cc{info.d & 3}"))))
                    case QuarkIntegerOpcode.orcc:  # or flag
                        il.append(il.set_flag(il.arch.get_flag_index(f"cc{info.a & 3}"), il.or_expr(0, il.flag(f"cc{info.c & 3}"), il.flag(f"cc{info.d & 3}"))))
                    case QuarkIntegerOpcode.xorcc:  # xor flag
                        il.append(il.set_flag(il.arch.get_flag_index(f"cc{info.a & 3}"), il.xor_expr(0, il.flag(f"cc{info.c & 3}"), il.flag(f"cc{info.d & 3}"))))
                    case QuarkIntegerOpcode.bp:  # breakpoint (not implemented in vm)
                        il.append(il.breakpoint())
                    case _:
                        il.append(il.unimplemented())
            case QuarkOpcode.cmp:  # unsigned comparisons
                cmp_op = QuarkCompareOpcode(info.b & 7)
                match cmp_op:
                    case QuarkCompareOpcode.lt:
                        il.append(il.sub(4, ra_expr(), cval(), flags=f"cmp.lt.cc{info.b >> 3}"))
                    case QuarkCompareOpcode.le:
                        il.append(il.sub(4, ra_expr(), cval(), flags=f"cmp.le.cc{info.b >> 3}"))
                    case QuarkCompareOpcode.ge:
                        il.append(il.sub(4, ra_expr(), cval(), flags=f"cmp.ge.cc{info.b >> 3}"))
                    case QuarkCompareOpcode.gt:
                        il.append(il.sub(4, ra_expr(), cval(), flags=f"cmp.gt.cc{info.b >> 3}"))
                    case QuarkCompareOpcode.eq:
                        il.append(il.sub(4, ra_expr(), cval(), flags=f"cmp.eq.cc{info.b >> 3}"))
                    case QuarkCompareOpcode.ne:
                        il.append(il.sub(4, ra_expr(), cval(), flags=f"cmp.ne.cc{info.b >> 3}"))
                    case QuarkCompareOpcode.nz:
                        il.append(il.and_expr(4, ra_expr(), cval(), flags=f"cmp.nz.cc{info.b >> 3}"))
                    case QuarkCompareOpcode.z:
                        il.append(il.and_expr(4, ra_expr(), cval(), flags=f"cmp.z.cc{info.b >> 3}"))
                    case _:
                        il.append(il.unimplemented())
            case QuarkOpcode.icmp:  # signed comparisons
                cmp_op = QuarkCompareOpcode(info.b & 7)
                match cmp_op:
                    case QuarkCompareOpcode.lt:
                        il.append(il.sub(4, ra_expr(), cval(), flags=f"icmp.lt.cc{info.b >> 3}"))
                    case QuarkCompareOpcode.le:
                        il.append(il.sub(4, ra_expr(), cval(), flags=f"icmp.le.cc{info.b >> 3}"))
                    case QuarkCompareOpcode.ge:
                        il.append(il.sub(4, ra_expr(), cval(), flags=f"icmp.ge.cc{info.b >> 3}"))
                    case QuarkCompareOpcode.gt:
                        il.append(il.sub(4, ra_expr(), cval(), flags=f"icmp.gt.cc{info.b >> 3}"))
                    case QuarkCompareOpcode.eq:
                        il.append(il.sub(4, ra_expr(), cval(), flags=f"icmp.eq.cc{info.b >> 3}"))
                    case QuarkCompareOpcode.ne:
                        il.append(il.sub(4, ra_expr(), cval(), flags=f"icmp.ne.cc{info.b >> 3}"))
                    case QuarkCompareOpcode.nz:
                        il.append(il.and_expr(4, ra_expr(), cval(), flags=f"icmp.nz.cc{info.b >> 3}"))
                    case QuarkCompareOpcode.z:
                        il.append(il.and_expr(4, ra_expr(), cval(), flags=f"icmp.z.cc{info.b >> 3}"))
                    case _:
                        il.append(il.unimplemented())
            case _:
                il.append(il.unimplemented())

        if after is not None:
            # Label after the instruction, jumping here will skip execution
            il.mark_label(after)

        return 4

    # ------------------------------------------------------------------------------------
    # Flag callbacks

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
            # `nz` condition: Compare if the AND of two values is non-zero
            case 'cmp.nz.cc0' | 'icmp.nz.cc0' | \
                 'cmp.nz.cc1' | 'icmp.nz.cc1' | \
                 'cmp.nz.cc2' | 'icmp.nz.cc2' | \
                 'cmp.nz.cc3' | 'icmp.nz.cc3':
                return il.compare_not_equal(
                    4,
                    il.and_expr(
                        4,
                        get_expr_for_register_or_constant(4, operands[0]),
                        get_expr_for_register_or_constant(4, operands[1])
                    ),
                    il.const(4, 0)
                )
            # `z` condition: Compare if the AND of two values is zero
            case 'cmp.z.cc0' | 'icmp.z.cc0' | \
                 'cmp.z.cc1' | 'icmp.z.cc1' | \
                 'cmp.z.cc2' | 'icmp.z.cc2' | \
                 'cmp.z.cc3' | 'icmp.z.cc3':
                return il.compare_equal(
                    4,
                    il.and_expr(
                        4,
                        get_expr_for_register_or_constant(4, operands[0]),
                        get_expr_for_register_or_constant(4, operands[1])
                    ),
                    il.const(4, 0)
                )
            case 'addx':
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
            # In case these get spilled to temporary writes, need to implement flag write for all conditions
            case 'cmp.lt.cc0' | 'cmp.lt.cc1' | 'cmp.lt.cc2' | 'cmp.lt.cc3':
                return il.compare_unsigned_less_than(size, get_expr_for_register_or_constant(size, operands[0]), get_expr_for_register_or_constant(size, operands[1]))
            case 'icmp.lt.cc0' | 'icmp.lt.cc1' | 'icmp.lt.cc2' | 'icmp.lt.cc3':
                return il.compare_signed_less_than(size, get_expr_for_register_or_constant(size, operands[0]), get_expr_for_register_or_constant(size, operands[1]))
            case 'cmp.le.cc0' | 'cmp.le.cc1' | 'cmp.le.cc2' | 'cmp.le.cc3':
                return il.compare_unsigned_less_equal(size, get_expr_for_register_or_constant(size, operands[0]), get_expr_for_register_or_constant(size, operands[1]))
            case 'icmp.le.cc0' | 'icmp.le.cc1' | 'icmp.le.cc2' | 'icmp.le.cc3':
                return il.compare_signed_less_equal(size, get_expr_for_register_or_constant(size, operands[0]), get_expr_for_register_or_constant(size, operands[1]))
            case 'cmp.ge.cc0' | 'cmp.ge.cc1' | 'cmp.ge.cc2' | 'cmp.ge.cc3':
                return il.compare_unsigned_greater_equal(size, get_expr_for_register_or_constant(size, operands[0]), get_expr_for_register_or_constant(size, operands[1]))
            case 'icmp.ge.cc0' | 'icmp.ge.cc1' | 'icmp.ge.cc2' | 'icmp.ge.cc3':
                return il.compare_signed_greater_equal(size, get_expr_for_register_or_constant(size, operands[0]), get_expr_for_register_or_constant(size, operands[1]))
            case 'cmp.gt.cc0' | 'cmp.gt.cc1' | 'cmp.gt.cc2' | 'cmp.gt.cc3':
                return il.compare_unsigned_greater_than(size, get_expr_for_register_or_constant(size, operands[0]), get_expr_for_register_or_constant(size, operands[1]))
            case 'icmp.gt.cc0' | 'icmp.gt.cc1' | 'icmp.gt.cc2' | 'icmp.gt.cc3':
                return il.compare_signed_greater_than(size, get_expr_for_register_or_constant(size, operands[0]), get_expr_for_register_or_constant(size, operands[1]))
            case 'cmp.eq.cc0' | 'cmp.eq.cc1' | 'cmp.eq.cc2' | 'cmp.eq.cc3':
                return il.compare_equal(size, get_expr_for_register_or_constant(size, operands[0]), get_expr_for_register_or_constant(size, operands[1]))
            case 'icmp.eq.cc0' | 'icmp.eq.cc1' | 'icmp.eq.cc2' | 'icmp.eq.cc3':
                return il.compare_equal(size, get_expr_for_register_or_constant(size, operands[0]), get_expr_for_register_or_constant(size, operands[1]))
            case 'cmp.ne.cc0' | 'cmp.ne.cc1' | 'cmp.ne.cc2' | 'cmp.ne.cc3':
                return il.compare_not_equal(size, get_expr_for_register_or_constant(size, operands[0]), get_expr_for_register_or_constant(size, operands[1]))
            case 'icmp.ne.cc0' | 'icmp.ne.cc1' | 'icmp.ne.cc2' | 'icmp.ne.cc3':
                return il.compare_not_equal(size, get_expr_for_register_or_constant(size, operands[0]), get_expr_for_register_or_constant(size, operands[1]))
        return il.unimplemented()

    def get_semantic_flag_group_low_level_il(
        self, sem_group: Optional[SemanticGroupType], il: 'lowlevelil.LowLevelILFunction'
    ) -> 'lowlevelil.ExpressionIndex':
        match sem_group:  # Each Semantic Flag Group only tests one flag since conditional branches can only read one flag
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

    # ------------------------------------------------------------------------------------
    # Patching

    def convert_to_nop(self, data: bytes, addr: int = 0) -> Optional[bytes]:
        # No need to be fancy here, just repeat a sequence that does nothing
        # Could also set QuarkInstruction.cond = 1
        return b'\x00\x00\xc0\x17' * (len(data) // 4)

    # Never branch uses convert_to_nop

    # Convert to NOP does not have a callback. It will be available if the
    # selection does not have the "never branch" patch available.

    def is_never_branch_patch_available(self, data: bytes, addr: int = 0) -> bool:
        # Make sure the data is a conditional branch
        if len(data) != 4:
            return False
        info = QuarkInstruction(int.from_bytes(data, 'little'))
        return info.cond != 0

    def is_always_branch_patch_available(self, data: bytes, addr: int = 0) -> bool:
        if len(data) != 4:
            return False
        info = QuarkInstruction(int.from_bytes(data, 'little'))
        return info.cond != 0

    def is_invert_branch_patch_available(self, data: bytes, addr: int = 0) -> bool:
        if len(data) != 4:
            return False
        info = QuarkInstruction(int.from_bytes(data, 'little'))
        return info.cond != 0

    def is_skip_and_return_zero_patch_available(self, data: bytes, addr: int = 0) -> bool:
        # Make sure the data is a call
        if len(data) != 4:
            return False
        info = QuarkInstruction(int.from_bytes(data, 'little'))
        return info.op == QuarkOpcode.call or (info.op == QuarkOpcode.integer_group and info.b == QuarkIntegerOpcode.call)

    def is_skip_and_return_value_patch_available(self, data: bytes, addr: int = 0) -> bool:
        if len(data) != 4:
            return False
        info = QuarkInstruction(int.from_bytes(data, 'little'))
        return info.op == QuarkOpcode.call or (info.op == QuarkOpcode.integer_group and info.b == QuarkIntegerOpcode.call)

    def always_branch(self, data: bytes, addr: int = 0) -> Optional[bytes]:
        if len(data) != 4:
            return None
        info = QuarkInstruction(int.from_bytes(data, 'little'))
        info.cond = 0  # Clear conditional execution flags
        return info.instr.to_bytes(4, "little")

    def invert_branch(self, data: bytes, addr: int = 0) -> Optional[bytes]:
        if len(data) != 4:
            return None
        info = QuarkInstruction(int.from_bytes(data, 'little'))
        info.cond = info.cond ^ 1  # Toggle if the instruction is skipped
        return info.instr.to_bytes(4, "little")

    # Skip and return zero uses skip_and_return_value(0)

    def skip_and_return_value(self, data: bytes, addr: int, value: int) -> Optional[bytes]:
        info = QuarkInstruction(0)
        info.op = QuarkOpcode.ldi
        info.a = 1  # return reg is normally r1 (shouldn't this need calling convention support??)
        info.imm17 = value
        return info.instr.to_bytes(4, "little")

    # ------------------------------------------------------------------------------------
    # Assembler

    @Architecture.can_assemble.getter
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
                    raise ValueError(f"Unknown instruction: {line} / {tokens}")
            result += i.instr.to_bytes(4, "little")
            addr += 4
        return result

# ----------------------------------------------------------------------------------------
# Platform setup and initialization


class QuarkCallingConvention(CallingConvention):
    name = "qcall"
    caller_saved_regs = ['r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9', 'r10', 'r11', 'r12', 'r13', 'r14', 'r15']
    callee_saved_regs = ['r16', 'r17', 'r18', 'r19', 'r20', 'r21', 'r22', 'r23', 'r24', 'r25', 'r26', 'r27', 'r28']
    int_arg_regs = ['r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8']
    int_return_reg = 'r1'
    high_int_return_reg = 'r2'
    arg_regs_for_varargs = False  # varargs functions take all params on the stack


class QuarkSyscallCallingConvention(CallingConvention):
    name = "qsyscall"
    caller_saved_regs = ['r1', 'r2']  # syscall preserves everything but the result regs
    callee_saved_regs = ['r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9', 'r10', 'r11', 'r12', 'r13', 'r14', 'r15', 'r16', 'r17', 'r18', 'r19', 'r20', 'r21', 'r22', 'r23', 'r24', 'r25', 'r26', 'r27', 'r28']
    int_arg_regs = ['syscall_num', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8']
    int_return_reg = 'r1'
    high_int_return_reg = 'r2'
    eligible_for_heuristics = False  # Don't try to guess if a call is syscall


class LinuxQuarkPlatform(Platform):
    name = "linux-quark"
    type_file_path = str(Path(__file__).parent / "types" / "linux-quark.c")

    def view_init(self, view: BinaryView):
        if not isinstance(view, BinaryView):  # Fixed in >= 5.3
            view = BinaryView(handle=binaryninja.core.BNNewViewReference(view))
        # Add stdlib Type Library to every analysis since it's static linked
        view.add_type_library(TypeLibrary.from_name(self.arch, "stdlib"))

        # Source needs to be added _after_ the WARP containers load, but that is done asynchronously
        # So, doing it in view_init means we will most likely lose the race and run this after.
        # >= 5.3 should have a new way of handling WARP sigs but this works for now
        WarpContainer['User'].add_source(str(Path(__file__).parent / "signatures" / "quark_stdlib.warp"))


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

# Load all the bundled Type Libraries
for file in (Path(__file__).parent / "typelib").glob("*.bntl"):
    TypeLibrary.load_from_file(str(file))

# ----------------------------------------------------------------------------------------
# Workflow for improving signatures


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
        # !! Make an iterator of the old instructions, which we can advance to skip them
        # since our pattern replaces multiple instructions
        instructions = iter(range(old_block.start, old_block.end))
        for old_instr_index in instructions:
            old_instr: LowLevelILInstruction = old_llil[InstructionIndex(old_instr_index)]
            new_llil.set_current_address(old_instr.address, old_block.arch)

            # Replace instructions with this really cool match powered by python 3.10

            # Load the next two instructions so we have a sequence of 3 instructions
            if old_instr_index + 2 < old_block.end:
                old_next_instr: LowLevelILInstruction = old_llil[InstructionIndex(old_instr_index + 1)]
                old_next_instr_2: LowLevelILInstruction = old_llil[InstructionIndex(old_instr_index + 2)]
                match (old_instr, old_next_instr, old_next_instr_2):
                    # Match all 3 instructions at once
                    case (
                        # rA = const
                        # rB = <addr> + rA
                        # rA = rB
                        LowLevelILSetReg(dest=regA, src=LowLevelILConst(constant=const)),
                        LowLevelILSetReg(
                            dest=regB,
                            src=LowLevelILAdd(
                                left=LowLevelILConst(constant=const_2),
                                right=LowLevelILReg(src=regA_2)
                            )
                        ),
                        LowLevelILSetReg(dest=regA_3, src=LowLevelILReg(src=regB_2))
                    ) if const_2 == old_next_instr_2.address and regA == regA_2 == regA_3 and regB == regB_2:
                        # rA = <addr + const>
                        new_llil.append(
                            new_llil.set_reg(
                                old_instr.size,
                                regA,
                                new_llil.const(
                                    old_instr.size,
                                    const + const_2,
                                    loc=old_next_instr_2.source_location  # Using all instr locations for mappings
                                ),
                                loc=old_instr.source_location  # Using all instr locations for mappings
                            )
                        )
                        # rB = <addr + const>
                        new_llil.append(
                            new_llil.set_reg(
                                old_instr.size,
                                regB,
                                new_llil.const(
                                    old_instr.size,
                                    const + const_2,
                                    loc=old_next_instr_2.source_location  # Using all instr locations for mappings
                                ),
                                loc=old_next_instr.source_location  # Using all instr locations for mappings
                            )
                        )
                        # Adding a nop here fixes stack resolution on the third instruction in disassembly view
                        # Not sure why, but it works
                        new_llil.append(new_llil.nop(loc=old_next_instr_2.source_location))
                        # Skip the next two instructions in the IL function
                        # because we matched them above and are replacing them here
                        next(instructions)
                        next(instructions)
                        any_replaced = True
                        continue

            new_llil.append(old_instr.copy_to(new_llil))

    # Update analysis if we changed anything
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
                # Only for linux-quark platform
                # Theoretically we want "only for quark arch" but arch predicates don't exist
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

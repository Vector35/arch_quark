import enum
from typing import Optional, Tuple, List

from binaryninja import Architecture, RegisterInfo, InstructionInfo, InstructionTextToken, \
    InstructionTextTokenType, BinaryViewType, Endianness, BranchType


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
        tokens = []
        return tokens, 4

QuarkArch.register()
BinaryViewType['ELF'].register_arch(4242, Endianness.LittleEndian, Architecture['Quark'])


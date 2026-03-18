"""
RISC-V Vector Extension (RVV) Instruction Disassembler

This module provides functionality to disassemble RISC-V Vector Extension
instructions into human-readable format.

Be warned, this is a work in progress and may not be 100% accurate.

If a better way to resolve conflicts is found, please update the code accordingly.
This works for me so I will keep it this way but updates are welcome :)
"""

from typing import Optional, Tuple


def extract_fields(instruction: int) -> Tuple[int, int, int, int, int, int, int, int]:

    # page 21 of RISC-V V spec 1.0
    opcode = instruction & 0x7F          # bits [6:0]
    vd_rd = (instruction >> 7) & 0x1F    # bits [11:7]
    funct3 = (instruction >> 12) & 0x7   # bits [14:12]
    vs1_rs1 = (instruction >> 15) & 0x1F # bits [19:15]
    vs2 = (instruction >> 20) & 0x1F     # bits [24:20]
    vm = (instruction >> 25) & 0x1       # bit [25]
    funct6 = (instruction >> 26) & 0x3F  # bits [31:26]
    imm5 = vs1_rs1                       # bits [19:15]
    
    return opcode, funct6, vm, vs2, vs1_rs1, funct3, vd_rd, imm5


def get_operand_category(funct3: int) -> Optional[str]:
    
    # page 42 of RISC-V V spec 1.0
    category_map = {
        0b000: 'OPIVV',
        0b001: 'OPFVV',
        0b010: 'OPMVV',
        0b011: 'OPIVI',
        0b100: 'OPIVX',
        0b101: 'OPFVF',
        0b110: 'OPMVX',
        0b111: 'OPCFG',  # Configuration
    }
    return category_map.get(funct3)

# Instruction mnemoics from pages 95-98 of RISC-V V spec 1.0

def get_OPIVV_mnemonic(funct6: int, vs2: int, vm: int) -> Tuple[Optional[str], bool]:

    opcode_map = {
        0b000000: 'vadd',
        0b000010: 'vsub',
        0b000100: 'vminu',
        0b000101: 'vmin',
        0b000110: 'vmaxu',
        0b000111: 'vmax',
        0b001001: 'vand',
        0b001010: 'vor',
        0b001011: 'vxor',
        0b001100: 'vrgather',
        0b001110: 'vrgatherei16',
        
        0b010000: 'vadc',
        0b010001: 'vmadc',
        0b010010: 'vsbc',
        0b010011: 'vmsbc',
        0b010111: 'vmerge/vmv',
        0b011000: 'vmseq',
        0b011001: 'vmsne',
        0b011010: 'vmsltu',
        0b011011: 'vmslt',
        0b011100: 'vmsleu',
        0b011101: 'vmsle',
        
        0b100000: 'vsaddu',
        0b100001: 'vsadd',
        0b100010: 'vssubu',
        0b100011: 'vssub',
        0b100101: 'vsll',
        0b101100: 'vsmul',
        0b101000: 'vsrl',
        0b101001: 'vsra',
        0b101010: 'vssrl',
        0b101011: 'vssra',
        0b101100: 'vnsrl',
        0b101101: 'vnsra',
        0b101110: 'vnclipu',
        0b101111: 'vnclip',
        
        0b110000: 'vwredsumu',
        0b110001: 'vwredsum'
    }
    
    mnemonic = opcode_map.get(funct6)
    if mnemonic == "vmerge/vmv":
        if vm == 1 and vs2 == 0b00000:
            return ('vmv.v.v', True)
        return ('vmerge', False)
    
    return mnemonic, False

        
def get_OPIVX_mnemonic(funct6: int, vs2: int, vm: int) -> Tuple[Optional[str], bool]:
        
    opcode_map = {    
    0b000000: 'vadd',
    0b000010: 'vsub',
    0b000011: 'vrsub',
    0b000100: 'vminu',
    0b000101: 'vmin',
    0b000110: 'vmaxu',
    0b000111: 'vmax',
    0b001001: 'vand',
    0b001010: 'vor',
    0b001011: 'vxor',
    0b001100: 'vrgather',
    0b001110: 'vslideup',
    0b001111: 'vslidedown',
    
    0b010000: 'vadc',
    0b010001: 'vmadc',
    0b010010: 'vsbc',
    0b010011: 'vmsbc',
    0b010111: 'vmerge/vmv',
    0b011000: 'vmseq',
    0b011001: 'vmsne',
    0b011010: 'vmsltu',
    0b011011: 'vmslt',
    0b011100: 'vmsleu',
    0b011101: 'vmsle',
    0b011110: 'vmsgtu',
    0b011111: 'vmsgt',
    
    0b100000: 'vsaddu',
    0b100001: 'vsadd',
    0b100010: 'vssubu',
    0b100011: 'vssub',
    0b100101: 'vsll',
    0b101100: 'vsmul',
    0b101000: 'vsrl',
    0b101001: 'vsra',
    0b101010: 'vssrl',
    0b101011: 'vssra',
    0b101100: 'vnsrl',
    0b101101: 'vnsra',
    0b101110: 'vnclipu',
    0b101111: 'vnclip'
    }
    
    mnemonic = opcode_map.get(funct6)
    if mnemonic == "vmerge/vmv":
        if vm == 1 and vs2 == 0b00000:
            return ('vmv.v.x', True)
        return ('vmerge', False)
    
    return mnemonic, False
        
        
def get_OPIVI_mnemonic(funct6: int, vs2: int, vm: int) -> Tuple[Optional[str], bool]:    
     
    opcode_map = {
        0b000000: 'vadd',
        0b000011: 'vrsub',
        0b001001: 'vand',
        0b001010: 'vor',
        0b001011: 'vxor',
        0b001100: 'vrgather',
        0b001110: 'vslideup',
        0b001111: 'vslidedown',
        
        0b010000: 'vadc',
        0b010001: 'vmadc',
        0b010111: 'vmerge/vmv',
        0b011000: 'vmseq',
        0b011001: 'vmsne',
        0b011100: 'vmsleu',
        0b011101: 'vmsle',
        0b011110: 'vmsgtu',
        0b011111: 'vmsgt',
        
        0b100000: 'vsaddu',
        0b100001: 'vsadd',
        0b100101: 'vsll',
        
        0b100111: 'vmv',
        
        0b101000: 'vsrl',
        0b101001: 'vsra',
        0b101010: 'vssrl',
        0b101011: 'vssra',
        0b101100: 'vnsrl',
        0b101101: 'vnsra',
        0b101110: 'vnclipu',
        0b101111: 'vnclip'
    }
    
    mnemonic = opcode_map.get(funct6)
    if mnemonic == "vmerge/vmv":
        if vm == 1 and vs2 == 0b00000:
            return ('vmv.v.i', True)
        return ('vmerge', False)
    
    if mnemonic == 'vmv':
        return (mnemonic, True)
    
    return (mnemonic, False)


def get_OPMVV_mnemonic(funct6: int, vs1: int) -> Tuple[Optional[str], bool]:
 
    if funct6 == 0b010000 or funct6 == 0b010010 or funct6 == 0b010100:
        opcode_map = {
            # VWXUNARY0
            (0b010000, 0b00000): 'vmv.x.s',
            (0b010000, 0b10000): 'vcpop.m',
            (0b010000, 0b10001): 'vfirst.m',
            #VXUNARY0
            (0b010010, 0b00010): 'vzext.vf8',
            (0b010010, 0b00011): 'vsext.vf8',
            (0b010010, 0b00100): 'vzext.vf4',
            (0b010010, 0b00101): 'vsext.vf4',
            (0b010010, 0b00110): 'vzext.vf2',
            (0b010010, 0b00111): 'vsext.vf2',
            #VMUNARY0
            (0b010100, 0b00001): 'vmsbf.m',
            (0b010100, 0b00010): 'vmsof.m',
            (0b010100, 0b00011): 'vmsif.m',
            (0b010100, 0b10000): 'viota.m',
            (0b010100, 0b10001): 'vid.v', # Not sure about this one
        }
        return opcode_map.get((funct6, vs1)), True
    
    opcode_map = {
        0b000000: 'vredsum',
        0b000001: 'vredand',
        0b000010: 'vredor',
        0b000011: 'vredxor',
        0b000100: 'vredminu',
        0b000101: 'vredmin',
        0b000110: 'vredmaxu',
        0b000111: 'vredmax',
        0b001000: 'vaaddu',
        0b001001: 'vaadd',
        0b001010: 'vasubu',
        0b001011: 'vasub',
        
        # These should've been handeled earlier
        0b010000: 'VWXUNARY0',
        0b010010: 'VXUNARY0',
        0b010100: 'VMUNARY0',
        
        0b010111: 'vcompress',
        0b011000: 'vmandnot',
        0b011001: 'vmand',
        0b011010: 'vmor',
        0b011011: 'vmxor',
        0b011100: 'vmornot',
        0b011101: 'vmnand',
        0b011110: 'vmnor',
        0b011111: 'vmxnor',
        
        0b100000: 'vdivu',
        0b100001: 'vdiv',
        0b100010: 'vremu',
        0b100011: 'vrem',
        0b100100: 'vmulhu',
        0b100101: 'vmul',
        0b100110: 'vmulhsu',
        0b100111: 'vmulh',
        0b101001: 'vmadd',
        0b101011: 'vnmsub',
        0b101101: 'vmacc',
        0b101111: 'vnmsac',
        
        0b110000: 'vwaddu',
        0b110001: 'vwadd',
        0b110010: 'vwsubu',
        0b110011: 'vwsub',
        0b110100: 'vwaddu.w',
        0b110101: 'vwadd.w',
        0b110110: 'vwsubu.w',
        0b110111: 'vwsub.w',
        0b111000: 'vwmulu',
        0b111010: 'vwmulsu',
        0b111011: 'vwmul',
        0b111100: 'vwmaccu',
        0b111101: 'vwmacc',
        0b111111: 'vwmaccsu'
    }
    return (opcode_map.get(funct6), False)

def get_OPMVX_mnemonic(funct6: int, vs2: int) -> Tuple[Optional[str], bool]:
 
    if funct6 == 0b010000:
        opcode_map = {
            # VRXUNARY0
            (0b010000, 0b00000): 'vmv.s.x',
        }
        return (opcode_map.get((funct6, vs2)), True)
 
    opcode_map = {
        0b001000: 'vaaddu',
        0b001001: 'vaadd',
        0b001010: 'vasubu',
        0b001011: 'vasub',
        0b001110: 'vslide1up',
        0b001111: 'vslide1down',
        
        0b100000: 'vdivu',
        0b100001: 'vdiv',
        0b100010: 'vremu',
        0b100011: 'vrem',
        0b100100: 'vmulhu',
        0b100101: 'vmul',
        0b100110: 'vmulhsu',
        0b100111: 'vmulh',
        0b101001: 'vmadd',
        0b101011: 'vnmsub',
        0b101101: 'vmacc',
        0b101111: 'vnmsac',
        
        0b110000: 'vwaddu',
        0b110001: 'vwadd',
        0b110010: 'vwsubu',
        0b110011: 'vwsub',
        0b110100: 'vwaddu.w',
        0b110101: 'vwadd.w',
        0b110110: 'vwsubu.w',
        0b110111: 'vwsub.w',
        0b111000: 'vwmulu',
        0b111010: 'vwmulsu',
        0b111011: 'vwmul',
        0b111100: 'vwmaccu',
        0b111101: 'vwmacc',
        0b111110: 'vwmaccus',
        0b111111: 'vwmaccsu'
    }
    
    return (opcode_map.get(funct6), False)



def get_OPFVV_mnemonic(funct6: int, vs1: int) -> Tuple[Optional[str], bool]:
    
    if funct6 == 0b010000 or funct6 == 0b010010 or funct6 == 0b010011:
        opcode_map = {
            # VWFUNARY0
            (0b010000, 0b00000): 'vfmv.f.s',
            
            #VFUNARY0
            (0b010010, 0b00000): 'vfcvt.xu.f.v',
            (0b010010, 0b00001): 'vfcvt.x.f.v',
            (0b010010, 0b00010): 'vfcvt.f.xu.v',
            (0b010010, 0b00011): 'vfcvt.f.x.v',
            (0b010010, 0b00110): 'vfcvt.rtz.xu.f.v',
            (0b010010, 0b00111): 'vfcvt.rtz.x.f.v',
            
            (0b010010, 0b01000): 'vfwcvt.xu.f.v',
            (0b010010, 0b01001): 'vfwcvt.x.f.v',
            (0b010010, 0b01010): 'vfwcvt.f.xu.v',
            (0b010010, 0b01011): 'vfwcvt.f.x.v',
            (0b010010, 0b01100): 'vfwcvt.f.f.v',
            (0b010010, 0b01110): 'vfwcvt.rtz.xu.f.v',
            (0b010010, 0b01111): 'vfwcvt.rtz.x.f.v',
            
            (0b010010, 0b10000): 'vfncvt.xu.f.w',
            (0b010010, 0b10001): 'vfncvt.x.f.w',
            (0b010010, 0b10010): 'vfncvt.f.xu.w',
            (0b010010, 0b10011): 'vfncvt.f.x.w',
            (0b010010, 0b10100): 'vfncvt.f.f.w',
            (0b010010, 0b10101): 'vfncvt.rod.f.f.w',
            (0b010010, 0b10110): 'vfncvt.rtz.xu.f.w',
            (0b010010, 0b10111): 'vfncvt.rtz.x.f.w',
                      
            #VFUNARY1
            (0b010011, 0b00000): 'vfsqrt.v',
            (0b010011, 0b00100): 'vfrsqrt7.v',
            (0b010011, 0b00101): 'vfrec7.v',
            (0b010011, 0b10000): 'vfclass.v',
        }
        return (opcode_map.get((funct6, vs1)), True)
    
    opcode_map = {
        0b000000: 'vfadd',
        0b000001: 'vfredusum',
        0b000010: 'vfsub',
        0b000011: 'vfredosum',
        0b000100: 'vfmin',
        0b000101: 'vfredmin',
        0b000110: 'vfmax',
        0b000111: 'vfredmax',
        0b001000: 'vfsgnj',
        0b001001: 'vfsgnjn',
        0b001010: 'vfsgnjx',
        0b001110: 'vfslide1up',
        0b001111: 'vfslide1down',
        
        # Should've been handeled earlier
        0b010000: 'VWFUNARY0',
        0b010010: 'VFUNARY0',
        0b010011: 'VFUNARY1',
        
        0b011000: 'vmfeq', 
        0b011001: 'vmfle',
        0b011011: 'vmflt',
        0b011100: 'vmfne',
        
        0b100000: 'vfdiv',
        0b100100: 'vfmul',
        0b101000: 'vfmadd',
        0b101001: 'vfnmadd',
        0b101010: 'vfmsub',
        0b101011: 'vfnmsub',
        0b101100: 'vfmacc',
        0b101101: 'vfnmacc',
        0b101110: 'vfmsac',
        0b101111: 'vfnmsac',
        
        0b110000: 'vfwadd',
        0b110001: 'vfwredusum',
        0b110010: 'vfwsub',
        0b110011: 'vfwredosum',
        0b110100: 'vfwadd.w',
        0b110110: 'vfwsub.w',
        0b111000: 'vfwmul',
        0b111100: 'vfwmacc',
        0b111101: 'vfwnmacc',   
        0b111110: 'vfwmsac',
        0b111111: 'vfwnmsac',
    }
    return (opcode_map.get(funct6), False)

       
def get_OPFVF_mnemonic(funct6: int, vs2: int) -> Tuple[Optional[str], bool]:
        
    if funct6 == 0b010000:
        opcode_map = {
            # VRFUNARY0
            (0b010000, 0b00000): 'vfmv.s.f'
        }
        return (opcode_map.get((funct6, vs2)), True)
        
    opcode_map = { 
        0b000000: 'vfadd',
        0b000010: 'vfsub',
        0b000100: 'vfmin',
        0b000110: 'vfmax',
        0b001000: 'vfsgnj',
        0b001001: 'vfsgnjn',
        0b001010: 'vfsgnjx',
        0b001110: 'vfslide1up',
        0b001111: 'vfslide1down',
        
        0b010111: 'vfmerge',
        0b011000: 'vmfeq', 
        0b011001: 'vmfle',
        0b011011: 'vmflt',
        0b011100: 'vmfne',
        0b011101: 'vmfgt',
        0b011111: 'vmfge',
        
        0b100000: 'vfdiv',
        0b100001: 'vfrdiv',
        0b100100: 'vfmul',
        0b100111: 'vfrsub',
        0b101000: 'vfmadd',
        0b101001: 'vfnmadd',
        0b101010: 'vfmsub',
        0b101011: 'vfnmsub',
        0b101100: 'vfmacc',
        0b101101: 'vfnmacc',
        0b101110: 'vfmsac',
        0b101111: 'vfnmsac',
        
        0b110000: 'vfwadd',
        0b110010: 'vfwsub',
        0b110100: 'vfwadd.w',
        0b110110: 'vfwsub.w',
        0b111000: 'vfwmul',
        0b111100: 'vfwmacc',
        0b111101: 'vfwnmacc',   
        0b111110: 'vfwmsac',
        0b111111: 'vfwnmsac',

    }
    
    return (opcode_map.get(funct6), False)


def get_config_mnemonic(funct6: int, vs2: int, vs1_rs1: int) -> Tuple[Optional[str], bool]:

    if funct6 == 0b000000:
        if vs2 == 0b11111:
            return ('vsetvli', False)
        else:
            return ('vsetvl', False)
    elif funct6 == 0b100000:
        return ('vsetivli', False)
    
    return (None, False)


def get_mnemonic(funct6: int, category: str, vs2: int, vs1_rs1: int, vm: int) -> Tuple[Optional[str], bool]:

    if category == 'OPIVV':
        return get_OPIVV_mnemonic(funct6, vs2, vm)
    elif category == 'OPIVX':
        return get_OPIVX_mnemonic(funct6, vs2, vm)
    elif category == 'OPIVI':
        return get_OPIVI_mnemonic(funct6, vs2, vm)
    elif category == 'OPMVV':
        return get_OPMVV_mnemonic(funct6, vs1_rs1)
    elif category == 'OPMVX':
        return get_OPMVX_mnemonic(funct6, vs2)
    elif category == 'OPFVV':
        return get_OPFVV_mnemonic(funct6, vs1_rs1)
    elif category == 'OPFVF':
        return get_OPFVF_mnemonic(funct6, vs2)
    elif category == 'OPCFG':
        return get_config_mnemonic(funct6, vs2, vs1_rs1)
    return None, False


def decode_vtype(vtype: int, vll: int) -> str:

    if vll == 0b1:
        return "ILLEGAL"
    
    vlmul_raw = vtype & 0x7
    vsew = (vtype >> 3) & 0x7
    vta = (vtype >> 6) & 0x1
    vma = (vtype >> 7) & 0x1
    
    # e8  SEW=8b 
    # e16 SEW=16b 
    # e32 SEW=32b 
    # e64 SEW=64b 
    sew_map = {0: "e8", 1: "e16", 2: "e32", 3: "e64"}
    sew = sew_map.get(vsew)
    
    # mf8  # LMUL=1/8 
    # mf4  # LMUL=1/4 
    # mf2  # LMUL=1/2 
    # m1   # LMUL=1, assumed if m setting absent 
    # m2   # LMUL=2 
    # m4   # LMUL=4 
    # m8   # LMUL=8
    lmul_map = {
        0: "m1", 1: "m2", 2: "m4", 3: "m8",
        4: "--reserved--", 5: "mf8", 6: "mf4", 7: "mf2"
    }
    lmul = lmul_map.get(vlmul_raw)
    
    ta = "tu" if vta == 0 else "ta"
    ma = "mu" if vma == 0 else "ma"
    
    return f"{sew}, {lmul}, {ta}, {ma}"

def format_OPCFG(instruction, vd_rd, vs1_rs1, vs2) -> str:
    
    # vsetvli
    if ((instruction >> 31) & 0x1) == 0b0:
        zimm = (instruction >> 20) & 0x7FF # bits [30:20]
        vtype = zimm & 0x7FF  # bits [30:20]
        vtype_str = decode_vtype(vtype, (vtype >> 10) & 0x1)
        return f"vsetvli x{vd_rd}, x{vs1_rs1}, {vtype_str}"
    
    # vsetivli
    elif ((instruction >> 30) & 0x3) == 0b11:
        uimm = vs1_rs1  # bits [19:15]
        vtypei = (instruction >> 20) & 0x3FF  # bits [29:20]
        vtype_str = decode_vtype(vtypei, (vtypei >> 9) & 0x1)
        return f"vsetivli x{vd_rd}, {uimm}, {vtype_str}"
    
    # vsetvl
    elif ((instruction >> 25) & 0x7F) == 0b1000000:
        return f"vsetvl x{vd_rd}, x{vs1_rs1}, x{vs2}"
    
    else:
        return "INVALID OPCFG"

# Page 29-39 of RISC-V V spec 1.0
def get_load_store_mnemonic(opcode: int, width: int, mop: int, mew: int, nf: int, lumop_sumop_rs2_vs2: int) -> Optional[str]:
    is_load = (opcode == 0x07)
    is_store = (opcode == 0x27)
    
    if not (is_load or is_store):
        return None
    
    eew_map = {
        0b000: "8",
        0b101: "16",
        0b110: "32",
        0b111: "64",
    }

    eew = eew_map.get(width)
    if eew is None:
        return None
    #     # Scalar FP loads/stores are not supported since they are not vector instructions but for some reason are mentioned in the spec
    #     if width == 0b001:
    #         return "flh" if is_load else "fsh"
    #     elif width == 0b010:
    #         return "flw" if is_load else "fsw"
    #     elif width == 0b011:
    #         return "fld" if is_load else "fsd"
    #     elif width == 0b100:
    #         return "flq" if is_load else "fsq"
    #     return None
    
    nfields = nf + 1
    
    if is_load:
        if mop == 0b00:  # unit-stride
            if lumop_sumop_rs2_vs2 == 0b00000:
                if nf == 0:
                    return f"vle{eew}"
                else:
                    return f"vlseg{nfields}e{eew}"
            elif lumop_sumop_rs2_vs2 == 0b01000:
                return f"vl{nfields}re{eew}"
            elif lumop_sumop_rs2_vs2 == 0b01011:
                return "vlm"
            elif lumop_sumop_rs2_vs2 == 0b10000:
                if nf == 0:
                    return f"vle{eew}ff"
                else:
                    return f"vlseg{nfields}e{eew}ff"
            else:
                if nf == 0:
                    return f"vle{eew}"
                else:
                    return f"vlseg{nfields}e{eew}"
                
        elif mop == 0b01:  # indexed-unordered
            if nf == 0:
                return f"vluxei{eew}"
            else:
                return f"vluxseg{nfields}ei{eew}"
        elif mop == 0b10:  # strided
            if nf == 0:
                return f"vlse{eew}"
            else:
                return f"vlsseg{nfields}e{eew}"
        elif mop == 0b11:  # indexed-ordered
            if nf == 0:
                return f"vloxei{eew}"
            else:
                return f"vloxseg{nfields}ei{eew}"
    else:  # store
        if mop == 0b00:  # unit-stride
            if lumop_sumop_rs2_vs2 == 0b00000:
                if nf == 0:
                    return f"vse{eew}"
                else:
                    return f"vsseg{nfields}e{eew}"
            elif lumop_sumop_rs2_vs2 == 0b01000:
                return f"vs{nfields}r"
            elif lumop_sumop_rs2_vs2 == 0b01011:
                return "vsm"
            else:
                # Default to unit-stride
                if nf == 0:
                    return f"vse{eew}"
                else:
                    return f"vsseg{nfields}e{eew}"
        elif mop == 0b01:  # indexed-unordered
            if nf == 0:
                return f"vsuxei{eew}"
            else:
                return f"vsuxseg{nfields}ei{eew}"
        elif mop == 0b10:  # strided
            if nf == 0:
                return f"vsse{eew}"
            else:
                return f"vssseg{nfields}e{eew}"
        elif mop == 0b11:  # indexed-ordered
            if nf == 0:
                return f"vsoxei{eew}"
            else:
                return f"vsoxseg{nfields}ei{eew}"
    
    return None


def format_load_store(instruction: int, opcode: int, vd_vs3: int, width: int, rs1: int, vm: int) -> str:
    
    # bits [6:0] opcode 
    # bits [7:11] vd (destination of load) or vs3 (store data)
    # bits [12:14] width (func3)
    # bits [15:19] rs1 (base address)
    # bits [20:24] (lumop or sumop, rs2 (stride), vs2 (address offset))
    # bits [25] vm (mask)
    # bits [26:27] mop (memory operation type)
    # bit [28] mew (memory element width)
    # bits [29:31] nf (number of fields - 1)
    
    lumop_sumop_rs2_vs2 = (instruction >> 20) & 0x1F
    mop = (instruction >> 26) & 0x3
    mew = (instruction >> 28) & 0x1
    nf = (instruction >> 29) & 0x7
    
    mnemonic = get_load_store_mnemonic(opcode, width, mop, mew, nf, lumop_sumop_rs2_vs2)
    if mnemonic is None:
        return "UNKNOWN"
    
    # Whole register load: vl1re8.v v1, (x1) 
    # Whole register store: vs1r.v v1, (x1)
    # Mask load/store: vlm.v v1, (x1)
    if (mnemonic.startswith("vl") and "re" in mnemonic) or (mnemonic.startswith("vs") and mnemonic.endswith("r")) or (mnemonic in ["vlm", "vsm"]):
        return f"{mnemonic}.v v{vd_vs3}, (x{rs1})"
    
    # Strided segment: vlsseg3e8.v v1, (x1), x2 [, v0.t]
    # Strided non-segment: vlse64.v v1, (x1), x2 [, v0.t]
 
    elif (("sseg" in mnemonic or "lseg" in mnemonic) and mop == 0b10) or ("se" in mnemonic and mop == 0b10 and "seg" not in mnemonic) or ("xseg" in mnemonic) or ("xei" in mnemonic):
        if vm == 0:
            return f"{mnemonic}.v v{vd_vs3}, (x{rs1}), x{lumop_sumop_rs2_vs2}, v0.t"
        else:
            return f"{mnemonic}.v v{vd_vs3}, (x{rs1}), x{lumop_sumop_rs2_vs2}"
    
    # Indexed segment: vluxseg3ei32.v v1, (x1), v2 [, v0.t]
    # Indexed non-segment: vluxei64.v v1, (x1), v2 [, v0.t]  
    elif ("xseg" in mnemonic) or ("xei" in mnemonic):
        if vm == 0:
            return f"{mnemonic}.v v{vd_vs3}, (x{rs1}), v{lumop_sumop_rs2_vs2}, v0.t"
        else:
            return f"{mnemonic}.v v{vd_vs3}, (x{rs1}), v{lumop_sumop_rs2_vs2}"

    # Unit-stride segment: vlseg3e8.v v1, (x1) [, v0.t]
    # Unit-stride non-segment: vle64.v v1, (x1) [, v0.t]
    elif ("seg" in mnemonic and (mnemonic.startswith("vl") or mnemonic.startswith("vs"))) or (mnemonic.startswith("vle") or mnemonic.startswith("vse")):
        if vm == 0:
            return f"{mnemonic}.v v{vd_vs3}, (x{rs1}), v0.t"
        else:
            return f"{mnemonic}.v v{vd_vs3}, (x{rs1})"
    
    # TODO scalar FP loads/stores are not part of the RISC-V V spec but are mentioned for some reason I won't be implementing them for now
    # Scalar FP loads/stores: fld f1, 0(x1)
    # elif mnemonic.startswith("fl") or mnemonic.startswith("fs"):
    #     imm = ((instruction >> 20) & 0xFFF) if is_load else (((instruction >> 25) & 0x7F) << 5) | ((instruction >> 7) & 0x1F)
    #     if imm & 0x800:
    #         imm = imm - 0x1000
    #     return f"{mnemonic} ft{vd_vs3}, {imm}(x{rs1})"
    
    # Generic format
    else:
        if vm == 0:
            return f"{mnemonic}.v v{vd_vs3}, (x{rs1}), v0.t"
        else:
            return f"{mnemonic}.v v{vd_vs3}, (x{rs1})"


def sign_extend_imm5(imm5: int) -> int:

    imm5 = imm5 & 0x1F
    if imm5 & 0x10:
        return imm5 - 32
    return imm5

def suffix_calculation(mnemonic: str, category: str, vm: int) -> str:

    base_suffix_map = {
        'OPIVV': '.vv',
        'OPIVX': '.vx',
        'OPIVI': '.vi',
        'OPFVV': '.vv',
        'OPFVF': '.vf',
        'OPMVV': '.vv',
        'OPMVX': '.vx',
        'OPCFG': '',
    }
    
    suffix = base_suffix_map.get(category, '')
    
    # Handle special cases for suffixes based on the mnemonic and category
    if mnemonic in ['vmadc', 'vmsbc', 'vadc', 'vsbc', 'vmerge', 'vfmerge']:
        if vm == 0:
            suffix += 'm'
            
    elif mnemonic in ['vnclipu', 'vnclip']:
        if vm == 0:
            if category == 'OPIVV':
                suffix = '.wv'
            if category == 'OPIVX':
                suffix = '.wx'
            elif category == 'OPIVI':
                suffix = '.wi'
                
    elif mnemonic[-2:] == '.w':
        suffix = 'v' if category in ['OPMVV', 'OPFVV'] else 'x' if category == 'OPMVX' else 'f'
    
    elif category in ['OPMVV', 'OPFVV']:
        if mnemonic in ['vredsum', 'vredmaxu', 'vredmax', 'vredminu', 'vredmin',
                        'vredand', 'vredor', 'vredxor', 
                        'vfredusum', 'vfredosum', 'vfredmin', 'vfredmax', 'vfwredusum', 'vfwredosum']:
            suffix = '.vs'
        elif mnemonic in ['vmand', 'vmnand', 'vmandn', 'vmxor', 
                         'vmor', 'vmnor', 'vmorn', 'vmxnor', 'vmandnot', 'vmornot']:
            suffix = '.mm'
        elif mnemonic == 'vcompress':
            suffix = '.vm'
    return suffix

def format_instruction(mnemonic: str, category: str, vd_rd: int, vs2: int,
                      vs1_rs1: int, imm5: int, vm: int, special: bool) -> str:

    # Special operations have a very unique format...
    if special:
        if mnemonic in ['vmv.x.s', 'vfmv.f.s', 'vcpop.m', 'vfirst.m']:
            return f"{mnemonic} x{vd_rd}, v{vs2}"
        
        elif mnemonic in ['vmv.s.x', 'vfmv.s.f', 'vmv.v.x']:
            return f"{mnemonic} v{vd_rd}, x{vs1_rs1}"
        
        elif mnemonic in ['vmv.v.v']:
            return f"{mnemonic} v{vd_rd}, v{vs1_rs1}"
        
        elif mnemonic in ['vmv.v.i']:
            return f"{mnemonic} v{vd_rd}, {sign_extend_imm5(imm5)}"
        
        elif mnemonic in ['vzext.vf8', 'vsext.vf8', 'vzext.vf4', 'vsext.vf4',
                          'vzext.vf2', 'vsext.vf2', 'vmsbf.m', 'vmsof.m', 'vmsif.m', 'viota.m',
                          'vfcvt.xu.f.v', 'vfcvt.x.f.v', 'vfcvt.f.xu.v', 
                          'vfcvt.f.x.v', 'vfcvt.rtz.xu.f.v', 'vfcvt.rtz.x.f.v',
                          'vfwcvt.xu.f.v','vfwcvt.x.f.v','vfwcvt.f.xu.v','vfwcvt.f.x.v','vfwcvt.f.f.v',
                          'vfwcvt.rtz.xu.f.v','vfwcvt.rtz.x.f.v',
                          'vfncvt.xu.f.w','vfncvt.x.f.w','vfncvt.f.xu.w','vfncvt.f.x.w','vfncvt.f.f.w',
                          'vfncvt.rod.f.f.w','vfncvt.rtz.xu.f.w','vfncvt.rtz.x.f.w',
                          'vfsqrt.v', 'vfrsqrt7.v', 'vfrec7.v', 'vfclass.v']:
            if vm == 0:
                return f"{mnemonic} v{vd_rd}, v{vs2}, v0.t"
            else:
                return f"{mnemonic} v{vd_rd}, v{vs2}"
            
        elif mnemonic == 'vid.v':
            if vm == 0:
                return f"{mnemonic} v{vd_rd}, v0.t"
            else:
                return f"{mnemonic} v{vd_rd}"
            
        elif mnemonic == 'vmv':
                nr = vs1_rs1 + 1
                return f"{mnemonic}{nr}r.v v{vd_rd}, v{vs2}"
        else:
            return f"{mnemonic} v{vd_rd}, v{vs2}"
    
    suffix = suffix_calculation(mnemonic, category, vm)
    full_mnemonic = f"{mnemonic}{suffix}"

    if category in ['OPIVV', 'OPMVV', 'OPFVV']:
        if vm == 0:
            return f"{full_mnemonic} v{vd_rd}, v{vs2}, v{vs1_rs1}, v0.t"
        else:
            return f"{full_mnemonic} v{vd_rd}, v{vs2}, v{vs1_rs1}"

    elif category in ['OPIVX', 'OPMVX']:
        if vm == 0:
            return f"{full_mnemonic} v{vd_rd}, v{vs2}, x{vs1_rs1}, v0.t"
        else:
            return f"{full_mnemonic} v{vd_rd}, v{vs2}, x{vs1_rs1}"

    elif category == 'OPIVI':
        imm_val = sign_extend_imm5(imm5)
        if vm == 0:
            return f"{full_mnemonic} v{vd_rd}, v{vs2}, {imm_val}, v0.t"
        else:
            return f"{full_mnemonic} v{vd_rd}, v{vs2}, {imm_val}"

    elif category == 'OPFVF':
        if vm == 0:
            return f"{full_mnemonic} v{vd_rd}, v{vs2}, x{vs1_rs1}, v0.t"
        else:
            return f"{full_mnemonic} v{vd_rd}, v{vs2}, x{vs1_rs1}"
    
    else:
        return "UNKNOWN FORMAT"
    

def disassemble_rvv(instruction: int) -> str:

    opcode, funct6, vm, vs2, vs1_rs1, funct3, vd_rd, imm5 = extract_fields(instruction)
    
    if opcode == 0x07 or opcode == 0x27:
        return format_load_store(instruction, opcode, vd_rd, funct3, vs1_rs1, vm)
    
    if opcode != 0x57:
        return "UNKNOWN opcode"
    
    category = get_operand_category(funct3)
    if category is None:
        return "UNKNOWN func3"
    
    if category == 'OPCFG':
        return format_OPCFG(instruction, vd_rd, vs1_rs1, vs2)
    
    mnemonic, special = get_mnemonic(funct6, category, vs2, vs1_rs1, vm)

    if mnemonic is None:
        return "UNKNOWN mnemonic"

    return format_instruction(mnemonic, category, vd_rd, vs2, vs1_rs1, imm5, vm, special)


def main():
    """
    Usage:
        python rvv_disassembler.py <instruction>
        python rvv_disassembler.py 0x5e0ec057
        python rvv_disassembler.py 1578102871
    """
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python rvv_disassembler.py <instruction>")
        print("  instruction can be in hex (0x...) or decimal format")
        print("\nExamples:")
        print("  python rvv_disassembler.py 0x5e0ec057")
        print("  python rvv_disassembler.py 1578102871")
        sys.exit(1)
    
    instruction_str = sys.argv[1].strip()
    
    try:
        if instruction_str.startswith('0x') or instruction_str.startswith('0X'):
            instruction = int(instruction_str, 16)
        else:
            instruction = int(instruction_str, 10)
        
        instruction = instruction & 0xFFFFFFFF
        
        result = disassemble_rvv(instruction)
        print(result)
        
    except ValueError as e:
        print(f"Error: Invalid instruction format '{instruction_str}'")
        print(f"  {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()


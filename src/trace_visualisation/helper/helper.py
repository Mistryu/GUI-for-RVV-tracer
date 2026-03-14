import json
import networkx as nx
from typing import Dict, List, Optional
from .rvv_disassembler import disassemble_rvv
from dash import html


def load_graph_from_json(json_file: str) -> nx.DiGraph:
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    graph = nx.DiGraph()
    for element in data['elements']:
        element_data = element.get('data', {})
        
        if 'source' in element_data:
            graph.add_edge(
                element_data['source'],
                element_data['target'],
                register=element_data.get('register')
            )
        else:
            graph.add_node(
                element_data['id'],
                instruction=element_data['instruction']
            )
    
    return graph


def build_elements(json_file: str, start: int = 0, end: Optional[int] = None, 
                  max_elements: int = 3000, filter_types: Optional[List[str]] = None,
                  is_execution_graph: bool = False) -> List[Dict]:
    
    graph = load_graph_from_json(json_file)
    
    # In order to correctly display execution graphs, we need to include all instruction types.
    if is_execution_graph:
        excluded_types = None
    else:
        type_map = {'reg': 1, 'csr': 2, 'ls': 3}
        excluded_types = {type_map[ft] for ft in filter_types if ft in type_map} if filter_types else None
    
    filtered_nodes = []
    for node_id, data in graph.nodes(data=True):
        if should_include_node(data['instruction'], start, end, excluded_types):
            filtered_nodes.append(node_id)
            if len(filtered_nodes) >= max_elements:
                break
    
    print(f"Selected {len(filtered_nodes)} nodes from total {graph.number_of_nodes()}")
    print(f"Graph has {graph.number_of_edges()} total edges")
    
    elements = []
    
    for node_id in filtered_nodes:
        instr = graph.nodes[node_id]['instruction']
        
        display_instr = instr['iterations'][0] if 'iterations' in instr else instr
        
        instr_number = display_instr.get('number', 0)
        instruction_hex = display_instr.get('instruction', '0x0')
        disassembled = disassemble_rvv(int(instruction_hex, 16))
        
        label = f"{instr_number}\n{disassembled}"
        
        elements.append({
            'data': {
                'id': node_id,
                'label': label,
                'type': display_instr.get('type'),
                'instruction': instr
            }
        })
    
    filtered_node_set = set(filtered_nodes)
    edge_count = 0
    for source, target, edge_data in graph.edges(data=True):
        if source in filtered_node_set and target in filtered_node_set:
            edge_count += 1
            elements.append({
                'data': {
                    'id': f"{source}-{target}",
                    'source': source,
                    'target': target,
                    'register': edge_data.get('register')
                }
            })
    
    return elements


def should_include_node(instr: Dict, start: int, end: Optional[int], 
                       excluded_types: Optional[set]) -> bool:
    executions = instr.get('iterations', [instr])
    
    for exec_instr in executions:
        exec_num = exec_instr.get('number', 0)
        exec_type = exec_instr.get('type')
        
        if end is not None and not (start <= exec_num < end):
            continue
        
        if excluded_types is not None and exec_type in excluded_types:
            continue
        
        return True
    return False

def decode_vtype(vtype) -> Dict[str, str]:
    if vtype is None or vtype == 'N/A':
        return {}
    
    try:
        vtype_int = int(vtype, 16)
    except (ValueError, TypeError):
        return {}
    
    vlmul_raw = vtype_int & 0x7
    vsew = (vtype_int >> 3) & 0x7
    vta = (vtype_int >> 6) & 0x1
    vma = (vtype_int >> 7) & 0x1
    
    sew_map = {0: "e8", 1: "e16", 2: "e32", 3: "e64"}
    lmul_map = {0: "1", 1: "2", 2: "4", 3: "8", 5: "1/8", 6: "1/4", 7: "1/2"}
    
    return {
        'vill': 'legal' if vtype.startswith('0x0') else 'illegal',
        'vma': 'agnostic' if vma else 'undisturbed',
        'vta': 'agnostic' if vta else 'undisturbed',
        'vsew': sew_map.get(vsew, f"reserved({vsew})"),
        'vlmul': lmul_map.get(vlmul_raw, f'reserved({vlmul_raw})')
    }


def decode_vcsr(vcsr) -> Dict[str, str]:
    if vcsr is None or vcsr == 'N/A':
        return {}
    
    try:
        vcsr_int = int(vcsr, 16)
    except (ValueError, TypeError):
        return {}
    
    vxsat = vcsr_int & 0x1
    vxrm = (vcsr_int >> 1) & 0x3
    
    vxrm_map = {
        0: "rnu (round-to-nearest-up)",
        1: "rne (round-to-nearest-even)",
        2: "rdn (round-down)",
        3: "rod (round-to-odd)"
    }
    
    return {
        'vxsat': 'saturated' if vxsat else 'no saturation',
        'vxrm': vxrm_map.get(vxrm, f"reserved({vxrm})")
    }

# SEW multipliers for each instruction: (vd, vs1, vs2)
# Default is (1, 1, 1)
# Source official RVV 1.0 specification
SEW_MULTIPLIERS = {
    
    # ------    WIDENING     -----------
    
    # Vector Arithmetic + Integer (vd=2*SEW, vs1=SEW, vs2=SEW) 
    'vwop.vv': (2.0, 1.0, 1.0), 'vwop.vx': (2.0, 1.0, 1.0),
    
    'vwaddu.vv': (2.0, 1.0, 1.0), 'vwaddu.vx': (2.0, 1.0, 1.0),
    'vwadd.vv': (2.0, 1.0, 1.0), 'vwadd.vx': (2.0, 1.0, 1.0),
    'vwsubu.vv': (2.0, 1.0, 1.0), 'vwsubu.vx': (2.0, 1.0, 1.0),
    'vwsub.vv': (2.0, 1.0, 1.0), 'vwsub.vx': (2.0, 1.0, 1.0),
    
    'vwmul.vv': (2.0, 1.0, 1.0), 'vwmul.vx': (2.0, 1.0, 1.0),
    'vwmulu.vv': (2.0, 1.0, 1.0), 'vwmulu.vx': (2.0, 1.0, 1.0),
    'vwmulsu.vv': (2.0, 1.0, 1.0), 'vwmulsu.vx': (2.0, 1.0, 1.0),
    
    'vwmaccu.vv':(2.0, 1.0, 1.0), 'vwmaccu.vx':(2.0, 1.0, 1.0),
    'vwmacc.vv': (2.0, 1.0, 1.0), 'vwmacc.vx': (2.0, 1.0, 1.0),
    'vwmaccsu.vv':(2.0, 1.0, 1.0), 'vwmaccsu.vx':(2.0, 1.0, 1.0),
    'vwmaccus.vx':(2.0, 1.0, 1.0),

    # (vd=2*SEW, vs1=SEW, vs2=2*SEW)
    'vwop.wv': (2.0, 1.0, 1.0), 'vwop.wx': (2.0, 1.0, 1.0),
    
    'vwaddu.wv': (2.0, 1.0, 2.0), 'vwaddu.wx': (2.0, 1.0, 2.0),
    'vwadd.wv': (2.0, 1.0, 2.0), 'vwadd.wx': (2.0, 1.0, 2.0),
    
    'vwsubu.wv': (2.0, 1.0, 2.0), 'vwsubu.wx': (2.0, 1.0, 2.0),
    'vwsub.wv': (2.0, 1.0, 2.0), 'vwsub.wx': (2.0, 1.0, 2.0),



    # Float (vd=2*SEW, vs1=SEW, vs2=SEW)
    'vfwadd.vv': (2.0, 1.0, 1.0), 'vfwadd.vf': (2.0, 1.0, 1.0),
    'vfwsub.vv': (2.0, 1.0, 1.0), 'vfwsub.vf': (2.0, 1.0, 1.0),
    
    'vfdiv.vv': (2.0, 1.0, 1.0), 'vfdiv.vf': (2.0, 1.0, 1.0),
    'vfrdiv.vf': (2.0, 1.0, 1.0),
    
    'vfwmul.vv': (2.0, 1.0, 1.0), 'vfwmul.vf': (2.0, 1.0, 1.0),
    
    'vfwmacc.vv':(2.0, 1.0, 1.0), 'vfwmacc.vf':(2.0, 1.0, 1.0),
    'vfwnmacc.vv':(2.0, 1.0, 1.0), 'vfwnmacc.vf':(2.0, 1.0, 1.0),
    'vfwmsac.vv':(2.0, 1.0, 1.0), 'vfwmsac.vf':(2.0, 1.0, 1.0),
    'vfwnmsac.vv':(2.0, 1.0, 1.0), 'vfwnmsac.vf':(2.0, 1.0, 1.0),

    # (vd=2*SEW, vs1=SEW, vs2=2*SEW)
    'vfwadd.wv': (2.0, 1.0, 2.0), 'vfwadd.wf': (2.0, 1.0, 2.0),
    'vfwsub.wv': (2.0, 1.0, 2.0), 'vfwsub.wf': (2.0, 1.0, 2.0),


    # Float converts (vd=2*SEW, vs2=SEW, no vs1) page 72
    'vfwcvt.xu.f.v': (2.0, 1.0, 1.0),
    'vfwcvt.x.f.v': (2.0, 1.0, 1.0),
    'vfwcvt.rtz.xu.f.v': (2.0, 1.0, 1.0),
    'vfwcvt.rtz.x.f.v': (2.0, 1.0, 1.0),
    'vfwcvt.f.xu.v': (2.0, 1.0, 1.0),
    'vfwcvt.f.x.v': (2.0, 1.0, 1.0),
    'vfwcvt.f.f.v': (2.0, 1.0, 1.0),


    # Vector Widening Integer Reduction Instructions (vd=2*SEW, vs1=2*SEW, vs2=SEW)
    'vwredsumu.vs': (2.0, 2.0, 1.0),
    'vwredsum.vs': (2.0, 2.0, 1.0),
    
    
    # Vector Widening Floating-Point Reduction Instructions (vd=2*SEW, vs1=2*SEW, vs2=SEW)
    'vfwredusum.vs': (2.0, 2.0, 1.0),
    'vfwredosum.vs': (2.0, 2.0, 1.0),



    # ------    NARROWING     -----------

    # Arithmetic (vd=SEW, vs1=SEW, vs2=2*SEW)
    'vnop.wv': (1.0, 1.0, 2.0),
    'vnop.wx': (1.0, 1.0, 2.0),

    # Integer (vd=SEW, vs1=SEW, vs2=2*SEW)
    'vnsrl.wv': (1.0, 1.0, 2.0), 'vnsrl.wx': (1.0, 1.0, 2.0), 'vnsrl.wi': (1.0, 1.0, 2.0),
    'vnsra.wv': (1.0, 1.0, 2.0), 'vnsra.wx': (1.0, 1.0, 2.0), 'vnsra.wi': (1.0, 1.0, 2.0),
    
    'vnclipu.wv': (1.0, 1.0, 2.0), 'vnclipu.wx': (1.0, 1.0, 2.0), 'vnclipu.wi': (1.0, 1.0, 2.0),
    'vnclip.wv': (1.0, 1.0, 2.0), 'vnclip.wx': (1.0, 1.0, 2.0), 'vnclip.wi': (1.0, 1.0, 2.0),

    # Float converts (vd=SEW, vs2=2*SEW, no vs1)
    'vfncvt.xu.f.w': (1.0, 1.0, 2.0),
    'vfncvt.x.f.w': (1.0, 1.0, 2.0),
    'vfncvt.rtz.xu.f.w': (1.0, 1.0, 2.0),
    'vfncvt.rtz.x.f.w': (1.0, 1.0, 2.0),
    'vfncvt.f.xu.w': (1.0, 1.0, 2.0),
    'vfncvt.f.x.w': (1.0, 1.0, 2.0),
    'vfncvt.f.f.w': (1.0, 1.0, 2.0),
    'vfncvt.rod.f.f.w': (1.0, 1.0, 2.0),
    
    
    
    
    # ------    Special     -----------
    
    # Vector Integer Extension (vd=SEW, vs1=none, vs2=fraction) page 46
    'vzext.vf2': (1.0, 1.0, 0.5),
    'vsext.vf2': (1.0, 1.0, 0.5),
    'vzext.vf4': (1.0, 1.0, 0.25),
    'vsext.vf4': (1.0, 1.0, 0.25),
    'vzext.vf8': (1.0, 1.0, 0.125),
    'vsext.vf8': (1.0, 1.0, 0.125),

}

UNAFFECTED_BY_VL = {
    'vl1re8.v', 'vl1re16.v', 'vl1re32.v', 'vl1re64.v',
    'vl2re8.v', 'vl2re16.v', 'vl2re32.v', 'vl2re64.v',
    'vl4re8.v', 'vl4re16.v', 'vl4re32.v', 'vl4re64.v',
    'vl8re8.v', 'vl8re16.v', 'vl8re32.v', 'vl8re64.v',
    'vs1r.v', 'vs2r.v', 'vs4r.v', 'vs8r.v',
    # Whole-register moves ignore VL, VLMUL, VSEW entirely
    'vmv1r.v', 'vmv2r.v', 'vmv4r.v', 'vmv8r.v',
    # Scalar <-> vector element 0 moves: only element 0 is affected, VL does not gate writes
    'vmv.x.s', 'vmv.s.x', 'vfmv.f.s', 'vfmv.s.f',
}

CODE_STYLE = {
        'display': 'block',
        'fontFamily': 'monospace',
        'fontSize': '11px',
        'backgroundColor': '#f0f0f0',
        'padding': '8px',
        'borderRadius': '4px',
        'wordBreak': 'break-all',
        'whiteSpace': 'pre-wrap',
        'lineHeight': '1.6'
    }


def clean_hex(data: str) -> str:
    clean = data[2:] if data.startswith('0x') or data.startswith('0X') else data
    return ('0' + clean) if len(clean) % 2 != 0 else clean

def reverse_bytes(hex_str: str) -> str:
    clean = clean_hex(hex_str)
    bytes_list = [clean[i:i+2] for i in range(0, len(clean), 2)]
    reversed_bytes = bytes_list[::-1]
    return ''.join(reversed_bytes)


def parse_mask(mask: str) -> list:
    clean = clean_hex(mask)
    bytes_list = [clean[i:i+2] for i in range(0, len(clean), 2)]
    
    bits = []
    for byte_str in bytes_list:
        byte_val = int(byte_str, 16)
        for bit_pos in range(0, 8):  # LSB first within each byte
            bits.append((byte_val >> bit_pos) & 1)
    
    return bits


def get_sew_multiplier(instruction: str, reg_type: str) -> float:
    mnemonic = instruction.split()[0] if instruction else ''
    vd_mul, vs1_mul, vs2_mul = SEW_MULTIPLIERS.get(mnemonic, (1.0, 1.0, 1.0))
    if 'vd' in reg_type:
        return vd_mul
    elif 'vs1' in reg_type:
        return vs1_mul
    elif 'vs2' in reg_type:
        return vs2_mul
    return 1.0


def format_mask_data(mask: str, num_elements: int) -> html.Code:
    if not mask or mask == 'N/A':
        return html.Code('N/A', style=CODE_STYLE)

    bits = parse_mask(mask)
    spans = []
    for i in range(num_elements):
        bit = bits[i] if i < len(bits) else 0
        spans.append(html.Span(
            str(bit) + ' ',
            style={'color': '#000000' if bit else '#bbbbbb'}
        ))

    return html.Code(spans, style=CODE_STYLE)


def get_element_color(idx: int, elements_before: int, mask_bits: Optional[list], effective_vl: Optional[int], element_offset: int) -> str:
    global_element_idx = elements_before + idx
    if effective_vl is not None and global_element_idx >= effective_vl:
        return '#bbbbbb'
    if mask_bits is not None:
        bit_idx = element_offset + idx
        active = mask_bits[bit_idx] if bit_idx < len(mask_bits) else 0
        return '#000000' if active else '#bbbbbb'
    return '#000000'


def format_hex_data(data: Optional[str], sew: int, instruction: str, reg_type: str,
                    mask_bits: Optional[list] = None, element_offset: int = 0,
                    vl: Optional[int] = None, elements_before: int = 0) -> html.Div:

    if data is None or data == 'N/A':
        return html.Div(html.Code('N/A', style=CODE_STYLE))

    clean = clean_hex(data)
    mul = get_sew_multiplier(instruction, reg_type)
    chars_per_element = max(int(sew * 2 * mul), 1)
    elements = [reverse_bytes(clean[i:i + chars_per_element]) for i in range(0, len(clean), chars_per_element)]
    #elements = elements[::-1]  # Reverse to show higher indices first

    effective_vl = None if skips_VL(instruction) else vl

    # No mask or VL
    if mask_bits is None and effective_vl is None:
        hex_code = html.Code(' '.join(elements), style=CODE_STYLE)
        int_spans = []
        for element in elements:
            int_spans.append(html.Span(str(int(element, 16)) + ' ', style={'color': '#000000'}))
        int_code = html.Code(int_spans, style=CODE_STYLE)
        return html.Div([hex_code, int_code])

    hex_spans = []
    int_spans = []
    for idx, element in enumerate(elements):
        color = get_element_color(idx, elements_before, mask_bits, effective_vl, element_offset)
        hex_spans.append(html.Span(element + ' ', style={'color': color}))
        int_spans.append(html.Span(str(int(element, 16)) + ' ', style={'color': color}))

    return html.Div([
        html.Code(hex_spans, style=CODE_STYLE),
        html.Code(int_spans, style=CODE_STYLE),
    ])


def skips_VL(instruction: str) -> bool:
    mnemonic = instruction.split()[0] if instruction else ''
    return mnemonic in UNAFFECTED_BY_VL


def format_register_data(instruction: str, register: str, reg_type: str,
                         reg_value: str, sew: int = 1,
                         mask: Optional[str] = None, vl: Optional[int] = None) -> html.Div:


    mask_bits = parse_mask(mask) if mask is not None else None

    # Scalar register - 1 byte grouping
    if register.startswith('x'):
        return html.Div([
            html.P([html.Strong(f"{register} ({reg_type}):")], style={'marginBottom': '5px'}),
            format_hex_data(reg_value, 1, '', reg_type)
        ], style={'marginBottom': '15px'})


    # Mask register - show only vl relevant bits
    if 'mask' in reg_type:
        num_elements = vl if vl is not None else (
            len(clean_hex(reg_value)) * 4 if reg_value and reg_value != 'N/A' else 0
        )
        return html.Div([
            format_mask_data(reg_value, num_elements)
        ], style={'marginBottom': '15px'})

    effective_vl = None if skips_VL(instruction) else vl

    # Single vector register (LMUL=1)
    if not isinstance(reg_value, list):
        return html.Div([
            format_hex_data(reg_value, sew, instruction, reg_type,
                            mask_bits=mask_bits, element_offset=0,
                            vl=effective_vl, elements_before=0)
        ], style={'marginBottom': '15px'})


    # Vector register group (LMUL > 1)
    mul = get_sew_multiplier(instruction, reg_type)
    chars_per_element = int(sew * 2 * mul)

    base_num = int(register.replace('v', ''))
    children = []
    elements_before = 0

    for index, value in enumerate(reg_value):
        elements_in_reg = len(clean_hex(value)) // chars_per_element
        children.append(html.Div([
            html.P([html.Strong(f"v{base_num + index} [0 - {elements_in_reg - 1}]:")],
                   style={'marginBottom': '2px', 'marginTop': '5px'}),
            format_hex_data(value, sew, instruction, reg_type,
                            mask_bits=mask_bits, element_offset=elements_before,
                            vl=effective_vl, elements_before=elements_before)
        ]))
        elements_before += elements_in_reg

    return html.Div(children, style={'marginBottom': '15px'})



















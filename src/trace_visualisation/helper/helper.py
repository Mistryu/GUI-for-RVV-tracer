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


def format_hex_data(data: str, bytes_per_group: int = 2):
    groups = []
    for i in range(0, len(data), bytes_per_group * 2):
        groups.append(data[i:i + bytes_per_group * 2])
    
    formatted = ' '.join(groups)
    
    return html.Code(
        formatted,
        style={
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
    )
    

def format_register_data(register: str, reg_type: str, reg_value):
    if 'x' in register:
        return html.Div([
                    html.P([html.Strong(f"{register} ({reg_type}):")], style={'marginBottom': '5px'}),
                    format_hex_data(reg_value, bytes_per_group=1)
                ], style={'marginBottom': '15px'})
        
    base_reg = int(register.replace('v', ''))
    elements = []
    for index, value in enumerate(reg_value):
        elements.append(html.Div([
                    html.P([html.Strong(f"v{base_reg + index}:")], 
                    style={'marginBottom': '2px', 'marginTop': '5px'}),
                    format_hex_data(value, bytes_per_group=1)
]))
    return html.Div(elements, style={'marginBottom': '15px'})
    
    # TODO bytes per group should be determined by sew
    # Add converting to hex, int, unsigned int, float get element sie from sew and 


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

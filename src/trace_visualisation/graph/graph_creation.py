import json
import networkx as nx
from typing import Dict, List, Tuple, Set
from pathlib import Path
import sys
import argparse
import traceback

class ComputationGraphBuilder:
    def __init__(self):
        self.rvv_state = {
            'vl': None,
            'vtype': None,
            'vstart': None,
            'vcsr': None,
            'vlenb': None
        }

    def extract_vector_registers(self, instr: Dict) -> Tuple[Set[int], Set[int]]:
        sources = set()
        destinations = set()
        
        if 'vd' in instr and instr['vd'] is not None:
            vd = instr['vd']
            vd_data = instr.get('vd_data', [])
            num_dest_regs = len(vd_data) if isinstance(vd_data, list) else 1
            for i in range(num_dest_regs):
                destinations.add(vd + i)
        
        if 'vs1' in instr and instr['vs1'] is not None:
            vs1 = instr['vs1']
            vs1_data = instr.get('vs1_data', [])
            num_vs1_regs = len(vs1_data) if isinstance(vs1_data, list) else 1
            for i in range(num_vs1_regs):
                sources.add(vs1 + i)
        
        if 'vs2' in instr and instr['vs2'] is not None:
            vs2 = instr['vs2']
            vs2_data = instr.get('vs2_data', [])
            num_vs2_regs = len(vs2_data) if isinstance(vs2_data, list) else 1
            for i in range(num_vs2_regs):
                sources.add(vs2 + i)
        
        return sources, destinations
    
    def update_rvv_state(self, instr: Dict) -> None:
        if instr.get('type') == 2:
            if 'vl' in instr:
                self.rvv_state['vl'] = instr['vl']
            if 'vtype' in instr:
                self.rvv_state['vtype'] = instr['vtype']
            if 'vstart' in instr:
                self.rvv_state['vstart'] = instr['vstart']
            if 'vcsr' in instr:
                self.rvv_state['vcsr'] = instr['vcsr']
            if 'vlenb' in instr:
                self.rvv_state['vlenb'] = instr['vlenb']

    def build_computational_graph(self, trace: List[Dict]) -> nx.DiGraph:
        graph = nx.DiGraph()
        register_producers = {}
        
        for instr in trace:
            self.update_rvv_state(instr)
            
            instr_with_state = instr.copy()
            instr_with_state['rvv_state'] = self.rvv_state.copy()
            
            node_id = f"instr_{instr['number']}"
            graph.add_node(node_id, instruction=instr_with_state)
            
            sources, destinations = self.extract_vector_registers(instr)
            
            for src_reg in sources:
                if src_reg in register_producers:
                    producer_id = register_producers[src_reg]
                    if producer_id != node_id:
                        graph.add_edge(producer_id, node_id, register=src_reg)
            
            for dest_reg in destinations:
                register_producers[dest_reg] = node_id
        
        return graph

    def build_aggregated_computational_graph(self, trace: List[Dict]) -> nx.DiGraph:

        graph = nx.DiGraph()
        register_producers = {}
        pc_map = {}
        
        for instr in trace:
            self.update_rvv_state(instr)
            
            instr_with_state = instr.copy()
            instr_with_state['rvv_state'] = self.rvv_state.copy()
            
            pc = instr.get('pc')
            
            # Adding nodes
            if pc in pc_map:
                node_id = pc_map[pc]
                existing_instr = graph.nodes[node_id]['instruction']
                
                if 'iterations' not in existing_instr:
                    existing_instr['iterations'] = [existing_instr.copy()]
                    existing_instr['iteration_count'] = 1
                
                existing_instr['iterations'].append(instr_with_state)
                existing_instr['iteration_count'] += 1

                # TODO ask if the first instruction state should be updated with the latest one or not                
                # for key in instr_with_state:
                #     if key not in ['iterations', 'iteration_count']:
                #         existing_instr[key] = instr_with_state[key]
                
                graph.nodes[node_id]['instruction'] = existing_instr
            else:
                node_id = f"pc_{pc}"
                pc_map[pc] = node_id
                graph.add_node(node_id, instruction=instr_with_state)
            
            sources, destinations = self.extract_vector_registers(instr)
            
            # Adding edges
            for src_reg in sources:
                if src_reg in register_producers:
                    producer_id = register_producers[src_reg]
                    if producer_id != node_id:
                        graph.add_edge(producer_id, node_id, register=src_reg)
            
            for dest_reg in destinations:
                register_producers[dest_reg] = node_id
        
        return graph

    def build_execution_graph(self, trace: List[Dict]) -> nx.DiGraph:
        graph = nx.DiGraph()
        pc_map = {}
        prev_node_id = None
        
        for instr in trace:
            self.update_rvv_state(instr)
            
            instr_with_state = instr.copy()
            instr_with_state['rvv_state'] = self.rvv_state.copy()
            
            pc = instr.get('pc')
            
            if pc in pc_map:
                node_id = pc_map[pc]
                existing_instr = graph.nodes[node_id]['instruction']
                
                if 'iterations' not in existing_instr:
                    existing_instr['iterations'] = [existing_instr.copy()]
                    existing_instr['iteration_count'] = 1
                
                existing_instr['iterations'].append(instr_with_state)
                existing_instr['iteration_count'] += 1
                
                # TODO ask if we want this
                # for key in instr_with_state:
                #     if key not in ['iterations', 'iteration_count']:
                #         existing_instr[key] = instr_with_state[key]
                
                graph.nodes[node_id]['instruction'] = existing_instr
            else:
                node_id = f"pc_{pc}"
                pc_map[pc] = node_id
                graph.add_node(node_id, instruction=instr_with_state)
            
            if prev_node_id is not None and prev_node_id != node_id:
                if not graph.has_edge(prev_node_id, node_id):
                    graph.add_edge(prev_node_id, node_id, edge_type='execution_order')
            
            prev_node_id = node_id
        
        return graph
    
    def graph_to_json(self, graph: nx.DiGraph, output_file: str) -> None:
        
        elements = []
        for node_id in graph.nodes():
            instr = graph.nodes[node_id]['instruction']
            elements.append({
                'data': {
                    'id': node_id,
                    'instruction': instr
                }
            })
        
        for source, target, data in graph.edges(data=True):
            edge_data = {
                'id': f"{source}-{target}",
                'source': source,
                'target': target,
            }
            # Add any additional edge attributes. We can filter to only include the ones we are interested in in cytoscape later on so I will leave it in for now
            # TODO ask if we want to include this and add an option to filter in cytoscape. 
            if 'register' in data:
                edge_data['register'] = data['register']
            if 'edge_type' in data:
                edge_data['edge_type'] = data['edge_type']
            
            elements.append({'data': edge_data})
        
        json_data = {'elements': elements}
        with open(output_file, 'w') as f:
            json.dump(json_data, f, indent=2)
    
def main() -> None:
    parser = argparse.ArgumentParser(
        description='Build computational graphs from RISC-V vector instruction trace',
        epilog='''
Examples:
  %(prog)s                              # Build all three graphs from vector_trace.json
  %(prog)s trace.json                   # Build all three graphs from custom file
  %(prog)s -s                           # Build only standard computational graph
  %(prog)s -a                           # Build only aggregated computational graph
  %(prog)s -e                           # Build only execution graph
  %(prog)s trace.json -o my_graph.json  # Custom output name for standard graph

Graph types:
  Computational: Computational graph where edges represent register dependencies (computational_graph.json)
  
  Aggregated: Computational graph where instructions with the same pc are aggregated to represent loops (aggregated_computational_graph.json)
  
  Execution: Shows execution order with loop aggregation (execution_graph.json)
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        'input_file',
        nargs='?',
        default='vector_trace.json',
        help='Input JSON trace file (default: vector_trace.json)'
    )
    parser.add_argument(
        '-o1', '--output1',
        default='computational_graph.json',
        help='Output file for standard computational graph (default: computational_graph.json)'
    )
    parser.add_argument(
        '-o2', '--output2',
        default='aggregated_computational_graph.json',
        help='Output file for aggregated computational graph (default: aggregated_computational_graph.json)'
    )
    parser.add_argument(
        '-o3', '--output3',
        default='execution_graph.json',
        help='Output file for execution graph (default: execution_graph.json)'
    )
    parser.add_argument(
        '-rs', '--remove-standard',
        action='store_true',
        default=False,
        help='Build only standard computational graph'
    )
    parser.add_argument(
        '-ra', '--remove-aggregated',
        action='store_true',
        default=False,
        help='Build only aggregated computational graph'
    )
    parser.add_argument(
        '-re', '--remove-execution',
        action='store_true',
        default=False,
        help='Build only execution graph'
    )
    
    args = parser.parse_args()
    
    json_file = args.input_file
    
    if not Path(json_file).exists():
        print(f"Error: Input file '{json_file}' not found", file=sys.stderr)
        sys.exit(1)
    
    build_standard = not args.remove_standard
    build_aggregated = not args.remove_aggregated
    build_execution = not args.remove_execution
    
    builder = ComputationGraphBuilder()
    
    try:
        with open(json_file, 'r') as f:
            trace = json.load(f)
    
        if build_standard:
            print("Building standard computational graph...")
            graph = builder.build_computational_graph(trace)
            builder.graph_to_json(graph, args.output1)
            
            print(f"  Nodes: {graph.number_of_nodes()}")
            print(f"  Edges: {graph.number_of_edges()}")
            print()
        
        if build_aggregated:
            builder.rvv_state = {
                'vl': None,
                'vtype': None,
                'vstart': None,
                'vcsr': None,
                'vlenb': None
            }
            
            print("Building aggregated computational graph...")
            agg_graph = builder.build_aggregated_computational_graph(trace)
            builder.graph_to_json(agg_graph, args.output2)
            
            print(f"  Nodes: {agg_graph.number_of_nodes()}")
            print(f"  Edges: {agg_graph.number_of_edges()}")
            print()
        
        if build_execution:
            builder.rvv_state = {
                'vl': None,
                'vtype': None,
                'vstart': None,
                'vcsr': None,
                'vlenb': None
            }
            
            print("Building execution graph...")
            exec_graph = builder.build_execution_graph(trace)
            builder.graph_to_json(exec_graph, args.output3)
            
            print(f"  Nodes: {exec_graph.number_of_nodes()}")
            print(f"  Edges: {exec_graph.number_of_edges()}")
        print("\nDone!")
    
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{json_file}': {e}", file=sys.stderr)
        sys.exit(1)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)
        
if __name__ == "__main__":
    main()
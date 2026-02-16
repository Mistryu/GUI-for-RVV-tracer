from typing import Optional
import dash
from dash import html, callback, Input, Output
import dash_cytoscape as cyto
from pathlib import Path
import argparse
import sys
from trace_visualisation.helper import build_elements, decode_vtype, decode_vcsr, format_register_data
from .style import CYTOSCAPE_STYLESHEET, LAYOUT_STYLES

cyto.load_extra_layouts()


def create_app(graph_files: dict, start: int = 0, end: Optional[int] = None, filter_types: Optional[list] = None):
    app = dash.Dash(__name__)
    
    valid_files = {name: path for name, path in graph_files.items() if Path(path).exists()}
    
    if not valid_files:
        print(f"Error: No valid graph files found", file=sys.stderr)
        print(f"Please run 'graph-creation' first to generate the graphs.", file=sys.stderr)
        sys.exit(1)
    
    initial_graph = None
    for preferred in ['computational', 'aggregated', 'execution']:
        if preferred in valid_files:
            initial_graph = preferred
            break
    
    try:
        initial_elements = build_elements(valid_files[initial_graph], start=start, end=end, filter_types=filter_types, is_execution_graph=(initial_graph == 'execution'))
        print(f"Loaded {len(initial_elements)} elements from {initial_graph} graph")
        print()
    except Exception as e:
        print(f"Error loading graph: {e}", file=sys.stderr)
        sys.exit(1)

    num_elements = len(initial_elements)
    is_large_graph = num_elements > 1000
    
    if is_large_graph:
        print(f"Warning: Large graph detected ({num_elements} elements)")
        print(f"Size shrunk to {num_elements} elements, but performance may still be slow and bugs may appear.")

    # Pretty good:
    # dagre
    # klay so far my favorite

    # Medium:
    # breathfirst

    # Bad:
    # cose-bilkent

    # Just past one of those in the layout field to check how it works
    # KLAY:
                    # layout={
                    #     'name': 'klay',
                    #     'klay': {
                    #         'direction': 'RIGHT',
                    #         'spacing': 50,
                    #         'nodePlacement': 'LINEAR_SEGMENTS'
                    #     },
                    #     'animate': False,
                    #     'fit': True
                    # },
    #
    # DAGRE:
    # {
    #     'name': 'dagre',
    #     'rankDir': 'LR',
    #     'nodeSep': 100,
    #     'rankSep': 150
    # },
    #
    # BREADTHFIRST:
    # {
    #     'name': 'breadthfirst',
    #     'directed': True,
    #     'spacingFactor': 1.5,
    #     'avoidOverlap': True
    # },
    #TODO comparison between these different program types:
    # Long big program 
    # Maybe a big loop with compuataions
    # Setup a benchmark 
    # Fix load/store instructions
    # Get ratio of rvv vs non rvv instructions 

    app.layout = html.Div([
        # Graph type selector buttons
        html.Div([
            html.Button('Computational', id='btn-computational', n_clicks=0,
                       style={**LAYOUT_STYLES['graph_button'], 
                              'backgroundColor': '#0066cc' if initial_graph == 'computational' else '#ffffff'}),
            html.Button('Aggregated', id='btn-aggregated', n_clicks=0,
                       style={**LAYOUT_STYLES['graph_button'],
                              'backgroundColor': '#0066cc' if initial_graph == 'aggregated' else '#ffffff'}),
            html.Button('Execution', id='btn-execution', n_clicks=0,
                       style={**LAYOUT_STYLES['graph_button'],
                              'backgroundColor': '#0066cc' if initial_graph == 'execution' else '#ffffff'}),
        ], style=LAYOUT_STYLES['button_container']),
        
        html.Div([
            # Left side - Graph
            html.Div([
                cyto.Cytoscape(
                    id='computation-graph',
                    elements=initial_elements,
                    style=LAYOUT_STYLES['cytoscape'],
                    layout={
                        'name': 'klay',
                        'klay': {
                            'direction': 'RIGHT',
                            'spacing': 50,
                            'nodePlacement': 'LINEAR_SEGMENTS',
                            'thoroughness': 10,
                            'direction': 'RIGHT',
                        },
                        'animate': False,
                        'fit': True
                    },
                    stylesheet=CYTOSCAPE_STYLESHEET,
                    userPanningEnabled=True,
                    userZoomingEnabled=True,
                    boxSelectionEnabled=False,
                    minZoom=0.1,
                    maxZoom=3.0,
                    wheelSensitivity=1,
                    responsive=True,
                )
            ], style=LAYOUT_STYLES['graph_panel']),
            
            # Right side - Details panel
            html.Div([
                html.Div(id='details-panel', style=LAYOUT_STYLES['details_content'])
            ], style=LAYOUT_STYLES['details_panel'])
        ], style=LAYOUT_STYLES['flex_wrapper'])
    ], style=LAYOUT_STYLES['container'])
    
    # TODO Expandable dropdown menu  
 
    # I added dynamic object at runtime which is valid python so the errors are just a typecheck
    app.graph_files = valid_files
    app.filter_params = {'start': start, 'end': end, 'filter_types': filter_types}

    @callback(
        [Output('computation-graph', 'elements'),
         Output('btn-computational', 'style'),
         Output('btn-aggregated', 'style'),
         Output('btn-execution', 'style')],
        [Input('btn-computational', 'n_clicks'),
         Input('btn-aggregated', 'n_clicks'),
         Input('btn-execution', 'n_clicks')],
        prevent_initial_call=True
    )
    def switch_graph(btn_comp, btn_agg, btn_exec):
        ctx = dash.callback_context
        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate
        
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        graph_map = {
            'btn-computational': 'computational',
            'btn-aggregated': 'aggregated',
            'btn-execution': 'execution'
        }
        
        selected_graph = graph_map.get(button_id)
        
        if not selected_graph or selected_graph not in app.graph_files:
            print(f"Warning: {selected_graph} graph not available")
            raise dash.exceptions.PreventUpdate
        
        try:
            elements = build_elements(
                app.graph_files[selected_graph],
                start=app.filter_params['start'],
                end=app.filter_params['end'],
                filter_types=app.filter_params['filter_types'],
                is_execution_graph=(selected_graph == 'execution')
            )
            print(f"Switched to {selected_graph} graph ({len(elements)} elements)")
            
        except Exception as e:
            print(f"Error loading {selected_graph} graph: {e}")
            raise dash.exceptions.PreventUpdate
        
        base_style = LAYOUT_STYLES['graph_button']
        active_style = {**base_style, 'backgroundColor': '#0066cc', 'color': '#ffffff'}
        inactive_style = {**base_style, 'backgroundColor': '#ffffff', 'color': '#333333'}
        
        comp_style = active_style if selected_graph == 'computational' else inactive_style
        agg_style = active_style if selected_graph == 'aggregated' else inactive_style
        exec_style = active_style if selected_graph == 'execution' else inactive_style
        
        return elements, comp_style, agg_style, exec_style

    @callback(
        Output('details-panel', 'children'),
        Input('computation-graph', 'selectedNodeData')
    )
    def update_details_panel(selected_nodes):
        if not selected_nodes:
            return html.Div([
                html.H3('Select an instruction to view details', style={'color': '#999999'})
            ], style={'padding': '20px'})
        
        node = selected_nodes[0]
        instr = node.get('instruction', {})
        
        is_loop = 'iterations' in instr
        
        #TODO rn I'm just showing data from first iteration of loop but add option to scroll though them
        if is_loop:
            iteration_count = instr.get('iteration_count', 1)
            display_instr = instr['iterations'][0]
        else:
            display_instr = instr
            iteration_count = 1
        
        instr_type = display_instr.get('type')
        instruction = node.get('label', display_instr.get('instruction', 'N/A')).splitlines()[1].strip() 
        lmul = display_instr.get('lmul', 1)
        
        details = []
        details.append(html.H3(instruction, style={'marginTop': 0, 'fontFamily': 'monospace', 'fontSize': '16px'}))

        if is_loop:
            details.append(
                html.Div([
                    html.P([
                        html.Strong('Loop: '),
                        f'Executed {iteration_count} times'
                    ], style={'color': '#0066cc', 'fontWeight': 'bold'})
                ])
            )
        
        details.extend([
            html.Hr(),
            html.Div([
                html.H4('Instruction Info', style={'marginBottom': '10px'}),
                html.P([html.Strong('Number: '), str(display_instr.get('number', 'N/A'))]),
                html.P([html.Strong('PC: '), display_instr.get('pc', 'N/A')]),
                html.P([html.Strong('Instruction: '), display_instr.get('instruction', 'N/A')]),
                html.P([html.Strong('LMUL: '), str(lmul)]),
            ]),
            html.Hr(),
        ])
        
        scalar_section = []
        scalar_section.append(html.H4('Scalar Registers', style={'marginBottom': '10px'}))
        
        if display_instr.get('rd') is not None:
            scalar_section.append(format_register_data(f"x{display_instr.get('rd')}", 'rd destination', display_instr.get('rd_value', 'N/A')))
        
        if display_instr.get('rs1') is not None:
            scalar_section.append(format_register_data(f"x{display_instr.get('rs1')}", 'rs1 source', display_instr.get('rs1_value', 'N/A')))
        
        if display_instr.get('rs2') is not None:
            scalar_section.append(format_register_data(f"x{display_instr.get('rs2')}", 'rs2 source', display_instr.get('rs2_value', 'N/A')))
    
        if len(scalar_section) > 1:
            details.extend(scalar_section)
        
        # Vector registers
        vec_section = []
        vec_section.append(html.H4('Vector Registers', style={'marginBottom': '10px'}))

        
        if 'vd' in display_instr and display_instr.get('vd') is not None:
            vec_section.append(html.H4('Destination vd:', style={'marginBottom': '10px'}))
            vec_section.append(format_register_data(f"v{display_instr.get('vd')}", 'vd destination', display_instr.get('vd_data', 'N/A')))
        
        if 'vs1' in display_instr and display_instr.get('vs1') is not None:
            vec_section.append(html.H4('Source vs1:', style={'marginBottom': '10px'}))
            vec_section.append(format_register_data(f"v{display_instr.get('vs1')}", 'vs1 source 1', display_instr.get('vs1_data', 'N/A')))

        if 'vs2' in display_instr and display_instr.get('vs2') is not None:
            vec_section.append(html.H4('Source vs2:', style={'marginBottom': '10px'}))
            vec_section.append(format_register_data(f"v{display_instr.get('vs2')}", 'vs2 source 2', display_instr.get('vs2_data', 'N/A')))  
        
        if len(vec_section) > 1:
            details.extend(vec_section)
        
        # RVV state 
        rvv_state = display_instr.get('rvv_state', {})
        if rvv_state:
            vtype_decoded = decode_vtype(rvv_state.get('vtype'))
            vcsr_decoded = decode_vcsr(rvv_state.get('vcsr'))
            
            rvv_section = [
                html.Hr(),
                html.H4('RVV State (at execution)', style={'marginBottom': '10px'}),
                
                # VL
                html.P([html.Strong('VL: '), 
                       str(rvv_state.get('vl', 'N/A'))],
                       style={'marginBottom': '8px'}),
                
                # VTYPE
                html.Div([
                    html.P([html.Strong('VTYPE: '), str(rvv_state.get('vtype', 'N/A'))]),
                    html.Ul([
                        html.Li(f"vill: {vtype_decoded.get('vill', 'N/A')}"),
                        html.Li(f"vma: {vtype_decoded.get('vma', 'N/A')}"),
                        html.Li(f"vta: {vtype_decoded.get('vta', 'N/A')}"),
                        html.Li(f"vsew: {vtype_decoded.get('vsew', 'N/A')}"),
                        html.Li(f"vlmul: {vtype_decoded.get('vlmul', 'N/A')}")
                    ], style={'marginLeft': '0px', 'fontSize': '16px', 'color': "#030303"})
                ], style={'marginBottom': '8px'}) if vtype_decoded else None,
                
                # VSTART
                html.P([html.Strong('VSTART: '), 
                       str(rvv_state.get('vstart', 'N/A'))],
                       style={'marginBottom': '8px'}),
                
                # VCSR
                html.Div([
                    html.P([html.Strong('VCSR: '), str(rvv_state.get('vcsr', 'N/A'))]),
                    html.Ul([
                        html.Li(f"vxsat (fixed-point saturation): {vcsr_decoded.get('vxsat', 'N/A')}"),
                        html.Li(f"vxrm (rounding mode): {vcsr_decoded.get('vxrm', 'N/A')}")
                    ], style={'marginLeft': '0px', 'fontSize': '16px', 'color': "#030303"})
                ], style={'marginBottom': '8px'}) if vcsr_decoded else None,
                
                # VLENB
                html.P([html.Strong('VLENB (Vector register length in bytes): '), 
                       str(rvv_state.get('vlenb', 'N/A'))],
                       style={'marginBottom': '100px'}),
            ]
            
            rvv_section = [item for item in rvv_section if item is not None]
            details.extend([html.Div(rvv_section)])
        
        return html.Div(details, style={'padding': '10px'})
    
    return app


def main():
    parser = argparse.ArgumentParser(
        description='Interactive visualization UI for RISC-V vector instruction computation graph',
        epilog='''
Examples:
  %(prog)s                              # Load graphs with default settings
  %(prog)s -s 1000 -e 2000              # Load instructions 1000-2000
  %(prog)s -t reg ls                    # Only show register and load/store instructions
  %(prog)s -t csr                       # Only show CSR instructions
  %(prog)s -s 0 -e 500 -t reg           # First 500 register instructions
  %(prog)s -i1 my_comp.json             # Use custom computational graph file

Default graph files:
  computational_graph.json
  aggregated_computational_graph.json
  execution_graph.json

Instruction types:
  reg : Register-register instructions (type 1)
  csr : Vector CSR configuration instructions (type 2)
  ls  : Load/Store instructions (type 3)
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '-i1', '--input-1',
        type=str,
        default='computational_graph.json',
        help='Computational graph JSON file (default: computational_graph.json)'
    )
    parser.add_argument(
        '-i2', '--input-2',
        type=str,
        default='aggregated_computational_graph.json',
        help='Aggregated computational graph JSON file (default: aggregated_computational_graph.json)'
    )
    parser.add_argument(
        '-i3', '--input-3',
        type=str,
        default='execution_graph.json',
        help='Execution graph JSON file (default: execution_graph.json)'
    )
    parser.add_argument(
        '-s', '--start',
        type=int,
        default=0,
        help='Starting instruction number (default: 0)'
    )
    parser.add_argument(
        '-e', '--end',
        type=int,
        default=None,
        help='Ending instruction number (default: None, loads all up to max_elements)'
    )
    parser.add_argument(
        '-t', '--types',
        nargs='+',
        choices=['reg', 'csr', 'ls'],
        default=['csr'],
        help='Filter by instruction types (default: show only reg and ls instructions)'
    )
    
    args = parser.parse_args()
    
    if args.start < 0:
        print("Error: start must be >= 0", file=sys.stderr)
        sys.exit(1)
    
    if args.end is not None and args.end <= args.start:
        print("Error: end must be greater than start", file=sys.stderr)
        sys.exit(1)
    
    graph_files = {
        'computational': args.input_1,
        'aggregated': args.input_2,
        'execution': args.input_3
    }
    
    existing_files = [name for name, path in graph_files.items() if Path(path).exists()]
    if not existing_files:
        print("Error: No valid graph files found", file=sys.stderr)
        sys.exit(1)
    
    print("Found graph files:")
    for name in existing_files:
        print(f"  {name}: {graph_files[name]}")
    print()
    
    app = create_app(graph_files, start=args.start, end=args.end, filter_types=args.types)
    app.run(debug=True)

if __name__ == '__main__':
    main()

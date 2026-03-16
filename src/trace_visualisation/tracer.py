import argparse
import sys
import subprocess
from pathlib import Path
from typing import Optional, List
import json


def run_graph_creation(
    input_file: str,
    output1: str,
    output2: str,
    output3: str,
    remove_standard: bool,
    remove_aggregated: bool,
    remove_execution: bool
):
    print("STEP 1: Building Computation Graphs")
    print()

    cmd = [
        sys.executable, '-m', 'trace_visualisation.graph.graph_creation',
        input_file,
        '-o1', output1,
        '-o2', output2,
        '-o3', output3
    ]
    
    if remove_standard:
        cmd.append('-rs')
    if remove_aggregated:
        cmd.append('-ra')
    if remove_execution:
        cmd.append('-re')
    
    try:
        subprocess.run(cmd, check=True, capture_output=False, text=True)
        print("Graph creation completed successfully")
        return True
    except Exception as e:
        print(f"Error during graph creation: {e}", file=sys.stderr)
        return False


def run_ui(
    input1: str,
    input2: str,
    input3: str,
    start: int,
    end: Optional[int],
    types: Optional[List[str]]
):
    print("STEP 2: Launching Visualization UI")
    print()
    cmd = [
        sys.executable, '-m', 'trace_visualisation.UI.app',
        '-i1', input1,
        '-i2', input2,
        '-i3', input3,
        '-s', str(start)
    ]
    
    if end is not None:
        cmd.extend(['-e', str(end)])
    
    if types:
        cmd.extend(['-t'] + types)
    
    try:
        subprocess.run(cmd, check=True)
        return True
    except Exception as e:
        print(f"Error while running UI: {e}", file=sys.stderr)
        return False


def validate_trace_file(input_file: str) -> bool:
    if not Path(input_file).exists():
        print(f"Error: Input trace file '{input_file}' not found", file=sys.stderr)
        return False
    
    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
            if not isinstance(data, list):
                print(f"Error: Trace file must contain a JSON array", file=sys.stderr)
                return False
            return True
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in trace file: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Tracer - RISC-V Vector Trace Visualization',
        epilog='''

Examples:
  %(prog)s --help            # Shows help menu
  %(prog)s trace.json                   # Create all graphs and launch UI 
  %(prog)s trace.json -s 0 -e 1000      # Visualize first 1000 instructions
  %(prog)s trace.json -t reg            # Remove register instructions
  %(prog)s trace.json --skip-ui         # Only build graphs, don't launch UI
  %(prog)s trace.json --skip-graphs     # Use existing graphs, just launch UI
  %(prog)s trace.json -rs               # Skip standard computational graph
  
Graph Types Built:
  - Computational Graph: Full computational graph where edges represent dependencies
  - Aggregated Graph: Loop-aggregated computational graph
  - Execution Graph: Sequential execution order with aggregated loops

Instruction Type Filters:
  reg : Register-register instructions (type 1)
  csr : Vector CSR configuration instructions (type 2) be default removed from computational graph and aggregated graph.
  ls  : Load/Store instructions (type 3)
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
        help='Output file for computational graph (default: computational_graph.json)'
    )
    parser.add_argument(
        '-o2', '--output2',
        default='aggregated_computational_graph.json',
        help='Output file for aggregated graph (default: aggregated_computational_graph.json)'
    )
    parser.add_argument(
        '-o3', '--output3',
        default='execution_graph.json',
        help='Output file for execution graph (default: execution_graph.json)'
    )
    
    # Graph creation options
    graph_group = parser.add_argument_group('graph creation options')
    graph_group.add_argument(
        '-rs', '--remove-standard',
        action='store_true',
        help='Skip building standard computational graph'
    )
    graph_group.add_argument(
        '-ra', '--remove-aggregated',
        action='store_true',
        help='Skip building aggregated computational graph'
    )
    graph_group.add_argument(
        '-re', '--remove-execution',
        action='store_true',
        help='Skip building execution graph'
    )
    
    # UI options
    ui_group = parser.add_argument_group('visualization options')
    ui_group.add_argument(
        '-s', '--start',
        type=int,
        default=0,
        help='Starting instruction number for visualization (default: 0)'
    )
    ui_group.add_argument(
        '-e', '--end',
        type=int,
        default=None,
        help='Ending instruction number for visualization (default: None)'
    )
    ui_group.add_argument(
        '-t', '--types',
        nargs='+',
        choices=['reg', 'csr', 'ls'],
        default=None,
        help='Filter by instruction types in UI (default: show all)'
    )
    
    control_group = parser.add_argument_group('pipeline control')
    control_group.add_argument(
        '--skip-graphs',
        action='store_true',
        help='Skip graph creation, only launch UI (use existing graphs)'
    )
    control_group.add_argument(
        '--skip-ui',
        action='store_true',
        help='Skip UI launch, only create graphs'
    )
    
    args = parser.parse_args()
    
    if args.skip_graphs and args.skip_ui:
        print("Error: Cannot skip both graphs and UI", file=sys.stderr)
        sys.exit(1)
    
    if args.start < 0:
        print("Error: start must be >= 0", file=sys.stderr)
        sys.exit(1)
    
    if args.end is not None and args.end <= args.start:
        print("Error: end must be greater than start", file=sys.stderr)
        sys.exit(1)
    
    print("RISC-V VECTOR TRACE VISUALIZATION PIPELINE")
    
    #Build graphs
    if not args.skip_graphs:
        if not validate_trace_file(args.input_file):
            sys.exit(1)
        
        success = run_graph_creation(
            args.input_file,
            args.output1,
            args.output2,
            args.output3,
            args.remove_standard,
            args.remove_aggregated,
            args.remove_execution
        )

    else:
        print("Skipping graph creation (using existing graphs)")
        print()
        
        graph_files = [args.output1, args.output2, args.output3]
        existing = [f for f in graph_files if Path(f).exists()]
        
        if not existing:
            print("Error: No existing graph files found", file=sys.stderr)
            sys.exit(1)
    
    #Build UI
    if not args.skip_ui:
        success = run_ui(
            args.output1,
            args.output2,
            args.output3,
            args.start,
            args.end,
            args.types
        )
        
        if not success:
            print("\nError at UI launch stage", file=sys.stderr)
            sys.exit(1)
    else:
        print("Skipping UI launch")
        print("Graph files created:")
        print(f"  - {args.output1}")
        print(f"  - {args.output2}")
        print(f"  - {args.output3}")

    print("\nSuccessfully completed all steps!")

if __name__ == '__main__':
    main()
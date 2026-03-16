# Computational Graph for RISC-V Vector Instructions

A visualization tool for RISC-V Vector Extension instruction traces, building dependency graphs and providing an interactive UI for analysis.

## Installation Steps

### 1. Install the package

```bash
pip install -e .
```

### 2. Verify installation

Check that the commands are available:

```bash
tracer --help

graph-creation --help

trace-ui --help
```

## Execution

Command to create graphs from the vector trace and run the ui:

```bash
tracer
```

If your graph is named vector_trace.json otherwise specify the name:

```bash
tracer my_trace.jon
```

The web interface will open at `http://127.0.0.1:8050/`

### How to use individual modules

First, generate the computation graph from your vector instruction trace:

If your trace file has the name vector_trace.json

```bash
graph-creation
```

Otherwise you must specify the name:

```bash
graph-creation your_trace.json
```

This will:

- Read the vector trace file

- Build the dependency graph

- By default export to 3 graphs ( computational_graph.json, aggregated_computational_graph.json and execution_graph.json)

### Launch Visualization UI

Launch the UI which will detect the graphs created previously.

```bash
trace-ui
```

The web interface will open at `http://127.0.0.1:8050/`

### Launch Both 
Launch the graph creation and the UI in one command:

```bash
tracer your_trace.json
```

### Additional options
Use --help to see all aviable flags

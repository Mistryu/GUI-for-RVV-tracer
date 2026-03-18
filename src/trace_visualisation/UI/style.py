CYTOSCAPE_STYLESHEET = [
    {
        'selector': 'node',
        'style': {
            'content': 'data(label)',
            'text-valign': 'center',
            'text-halign': 'center',
            'background-color': '#e6f2ff',
            'color': '#000000',
            'font-size': '10px',
            'font-family': 'monospace',
            'width': 'label',
            'height': 'label',
            'padding': '8px',
            'shape': 'roundrectangle',
            'text-wrap': 'wrap',
            'text-max-width': '160px',
            'border-width': '2px',
            'border-color': '#666666',
            'line-height': '1.2',
        }
    },
    {
        'selector': 'node[type = 1]',
        'style': {'background-color': '#90EE90'}
    },
    {
        'selector': 'node[type = 2]',
        'style': {'background-color': '#FFB366'}
    },
    {
        'selector': 'node[type = 3]',
        'style': {'background-color': '#D3D3D3'}
    },
    {
        'selector': 'node:selected',
        'style': {
            'border-color': '#FF4136',
            'border-width': '3px'
        }
    },
    {
        'selector': 'edge',
        'style': {
            'curve-style': 'bezier',
            'target-arrow-shape': 'triangle',
            'line-color': '#666666',
            'target-arrow-color': '#666666',
            'width': '2px',
            'arrow-scale': 1.5
        }
    },
    {
        'selector': 'edge:active',
        'style': {'overlay-opacity': 0}
    }
]

LAYOUT_STYLES = {
    'container': {
        'margin': 0,
        'padding': 0,
        'fontFamily': 'Arial, sans-serif',
        'position': 'fixed',
        'width': '100%',
        'height': '100vh',
        'overflow': 'hidden'
    },
    'button_container': {
        'position': 'absolute',
        'top': '10px',
        'left': '10px',
        'zIndex': 1000,
        'display': 'flex',
        'gap': '5px',
        'padding': '5px',
        'backgroundColor': 'rgba(255, 255, 255, 0.9)',
        'borderRadius': '5px',
        'boxShadow': '0 2px 5px rgba(0,0,0,0.2)'
    },
    'graph_button': {
        'padding': '8px 16px',
        'border': '1px solid #ddd',
        'borderRadius': '4px',
        'cursor': 'pointer',
        'fontSize': '14px',
        'fontWeight': '500',
        'transition': 'all 0.3s ease',
        'backgroundColor': '#ffffff',
        'color': '#333333'
    },
    'flex_wrapper': {
        'display': 'flex',
        'width': '100%',
        'height': '100vh'
    },
    'graph_panel': {
        'width': '70%',
        'height': '100vh',
        'borderRight': '1px solid #ddd'
    },
    'cytoscape': {
        'width': '100%',
        'height': '100%'
    },
    'details_panel': {
        'width': '30%',
        'height': '100vh',
        'backgroundColor': '#f9f9f9',
        'overflowY': 'auto',
        'overflowX': 'hidden'
    },
    'details_content': {
        'padding': '20px'
    }
}

import dash
from dash import Dash, html, dcc, dash_table, callback, callback_context
import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import Input, Output, State, ALL, MATCH
import plotly.graph_objects as go
import plotly.express as px
import dash_cytoscape as cyto
from dash.exceptions import PreventUpdate
import json

import pandas as pd

# Import computations
from app.computations.computations import (
    load_data,
    do_umap,
    preprocess_data
)

from app.computations.cyto_computations import (
    prepare_cyo_graph,
    create_cyo_stylesheet
)

# Initialize Dash app with Bootstrap theme
app = Dash(__name__,
           url_base_pathname='/',
           external_stylesheets=[dbc.themes.BOOTSTRAP])

# Read CSV
df = load_data()

# Preprocess data
df = preprocess_data(df)

# Data size limits
MAX_ROWS = 11000
if len(df) > MAX_ROWS:
    print(f'Limiting data from {len(df)} rows to {MAX_ROWS} rows')
    df = df.sample(MAX_ROWS, random_state=42)

def gen_content():
    return html.Div([
        # Header
        dbc.Navbar([
            dbc.Container([
                html.Div([
                    html.H1("Learning Dynamics Exploratory Analysis Tool", 
                        className="mb-0",
                        style={
                            'font-size': '1.0rem',
                            'font-weight': '550',
                            'font-family': '"Segoe UI", Arial, sans-serif',
                            'letter-spacing': '0.5px',
                            'color': '#333'
                        }
                    ),
                ], className="d-flex flex-column")
            ], fluid=True)
        ], 
            dark=False,
            color="light",
            className="mb-4 py-2",
            style={
                'box-shadow': '0 2px 4px rgba(0,0,0,0.1)',
                'background': '#f8f9fa',
                'padding-left': '2rem'
            }
        ),
        # Main content 
        dbc.Container([
            dbc.Row([
                # Left column for ALL filters
                dbc.Col([
                    html.H4('Filters', 
                           style={
                               'font-size': '1.1rem',
                               'font-weight': '500',
                               'color': '#444',
                               'margin-bottom': '0.5rem'
                           }),
                    html.Hr(style={'margin': '0.5rem 0'}),
                    
                    # UMAP Parameters
                    html.Label('UMAP Parameters'),
                    dbc.Row([
                        dbc.Col([
                            html.Label('n_neighbors'),
                            dcc.Input(
                                id='n-neighbors-input',
                                type='number',
                                value=15,
                                min=2,
                                max=100,
                                step=1,
                                style={'width': '100%'}
                            ),
                        ], width=6),
                        dbc.Col([
                            html.Label('min_dist'),
                            dcc.Input(
                                id='min-dist-input',
                                type='number',
                                value=0.1,
                                min=0.0,
                                max=1.0,
                                step=0.1,
                                style={'width': '100%'}
                            ),
                        ], width=6),
                    ]),
                    html.Br(),
                    
                    # Subject filter
                    html.Label('Subject ID'),
                    dcc.Dropdown(
                        id='subject-filter',
                        options=[{'label': str(id), 'value': id} for id in df['subject_id'].unique()],
                        multi=True,
                        placeholder='Select subjects...'
                    ),
                    html.Br(),
                    
                    # Stage filter
                    html.Label('Training Stage'),
                    dcc.Dropdown(
                        id='stage-filter',
                        options=[{'label': str(stage), 'value': stage} for stage in df['current_stage_actual'].unique()],
                        multi=True,
                        placeholder='Select stage...'
                    ),
                    html.Br(),

                    # Task filter
                    html.Label('Task'),
                    dcc.Dropdown(
                        id='task-filter',
                        options=[{'label': str(task), 'value': task} for task in df['task'].unique()],
                        multi=True,
                        placeholder='Select task...'
                    ),
                    html.Br(),
                    
                    # Session range filter
                    html.Label('Session Range'),
                    dcc.RangeSlider(
                        id='session-range',
                        min=df['session'].min(),
                        max=df['session'].max(),
                        step=1,
                        marks={i: str(i) for i in range(df['session'].min(), df['session'].max()+1, 5)},
                        value=[df['session'].min(), df['session'].max()]
                    ),
                        dbc.Card([
                        dbc.CardHeader('Processing State'),
                        dbc.CardBody(
                            id='processing-state',
                            style = {
                                'white-space': 'pre-line',
                                'font-family': 'monospace',
                                'font-size': '0.8rem',
                            }
                        )
                    ], className = "mt-4")
                ], width=2, style={'background-color': '#f8f9fa', 'padding': '20px', 'border-radius': '5px'}),

                # Right column for plot and info
                dbc.Col([
                    # Debug div to show callback execution
                    html.Div(id='debug-div', style={'display': 'none'}),
                    
                    # Plot container
                    html.Div(
                        id='dim_reduction_plot',
                        children=[
                            html.P("Initializing plot...", id='plot-status')
                        ],
                        style={'height': '80vh', 'margin-bottom': '20px'}
                    ),
                    
                    # Info panel
                    dbc.Card([
                        dbc.CardBody([
                            html.H5(
                                "Subject Information", 
                                className="card-title",
                                style={
                                    'font-size': '1.1rem',
                                    'font-weight': '500',
                                    'color': '#444'
                                }
                            ),
                            html.Div(
                                id='node-info', 
                                className="card-text",
                                children="Click a node to see subject information"
                            )
                        ])
                    ], 
                        className="mt-3",
                        style={
                            'box-shadow': '0 2px 4px rgba(0,0,0,0.1)',
                            'border': '1px solid #dee2e6'
                        }
                    )
                ], width=10)
            ], className='g-0')
        ], fluid=True)
    ])

# Layout
app.layout = html.Div([
    gen_content(),
])

@callback(
    [Output('dim_reduction_plot', 'children'),
     Output('processing-state', 'children')],
    [Input('subject-filter', 'value'),
     Input('stage-filter', 'value'),
     Input('task-filter', 'value'),
     Input('session-range', 'value'),
     Input('n-neighbors-input', 'value'),
     Input('min-dist-input', 'value')],
    prevent_initial_call=False
)
def update_dim_reduction_cytoscape(selected_subjects, 
                                 selected_stages, 
                                 selected_tasks, 
                                 session_range,
                                 n_neighbors,
                                 min_dist):
    try:
        filtered_df = df.copy()
        print(f"Initial dataframe shape: {filtered_df.shape}")

        # Apply filters
        if selected_subjects:
            filtered_df = filtered_df[filtered_df['subject_id'].isin(selected_subjects)]
        
        if selected_stages:
            filtered_df = filtered_df[filtered_df['current_stage_actual'].isin(selected_stages)]
        
        if selected_tasks:
            filtered_df = filtered_df[filtered_df['task'].isin(selected_tasks)]

        if session_range:
            filtered_df = filtered_df[
                (filtered_df['session'] >= session_range[0]) & 
                (filtered_df['session'] <= session_range[1])
            ]

        # Initialize variables
        nodes = None
        edges = None
        
        # Perform UMAP with user-specified parameters
        print(f"Starting UMAP computation with n_neighbors={n_neighbors}, min_dist={min_dist}")
        result_df = do_umap(filtered_df, n_neighbors=n_neighbors, min_dist=min_dist)
        status_message = f"UMAP completed with n_neighbors={n_neighbors}, min_dist={min_dist}"
        
        # Prepare cytoscape graph
        print("Preparing graph")
        nodes, edges = prepare_cyo_graph(result_df, filtered_df, result_df, 
                                       method='umap', 
                                       connect_by_column='task')
        print(f"Generated {len(nodes)} nodes and {len(edges)} edges")

        cyto_component = cyto.Cytoscape(
            id='dim-reduction-cytoscape',
            elements=nodes + edges,
            stylesheet=create_cyo_stylesheet(),
            style={'width': '100%', 'height': '800px'},
            layout={'name': 'preset'},
            minZoom=0.5,
            maxZoom=10,
            userZoomingEnabled=True,
            userPanningEnabled=True,
            boxSelectionEnabled=False,
            autounselectify=False,
        )
        
        return [cyto_component, f"{status_message}\nGenerated {len(nodes)} nodes and {len(edges)} edges"]

    except Exception as e:
        import traceback
        error_msg = f"Error in callback: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return [html.P(f"Error: {str(e)}"), error_msg]

@callback(
    Output('node-info', 'children'),
    Input('dim-reduction-cytoscape', 'tapNodeData')
)
def display_node_info(tapNodeData):
    if not tapNodeData:
        return "Click a node to see subject information"
    
    try:
        # Calculate colors for nodes and edges
        session_prop = float(tapNodeData['session_proportion'])

        # linear interpolation between blue (0,0,255) and red (255,0,0) NODES
        r = int(255 * session_prop)
        b = int(255 * (1 - session_prop))
        session_color = f'rgb({r}, 0, {b})'

        # Get task color
        colors = px.colors.qualitative.Set2
        all_possible_tasks = sorted(df['task'].unique())  # Sort to ensure consistent ordering
        master_color_map = {val: colors[i % len(colors)] for i, val in enumerate(all_possible_tasks)}
        task_color = master_color_map[tapNodeData['task']]

        # Debug logging
        print(f"Node info color assignment:")
        print(f"Task: {tapNodeData['task']}")
        print(f"Assigned color: {task_color}")
        print(f"All tasks: {all_possible_tasks}")

        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Strong("Subject ID: "),
                        html.Span(tapNodeData['subject_id'])
                    ], className="me-4"),
                ], width='auto'),

                dbc.Col([
                    html.Div([
                        html.Strong("Session: "),
                        html.Span(tapNodeData['session'])
                    ], className="me-4"),
                ], width='auto'),
                dbc.Col([
                    html.Div([
                        html.Strong("Session Proportion: "),
                        html.Span("{:.2f}".format(float(tapNodeData['session_proportion']))),
                        html.Div(style = {
                            'display': 'inline-block',
                            'marginLeft': '8px',
                            'width': '12px',
                            'height': '12px',
                            'backgroundColor': session_color,
                            'borderRadius': '50%',
                            'border': '1px solid #ccc',
                            'verticalAlign': 'middle'
                        })
                    ], className="me-4"),
                ], width='auto'),

                dbc.Col([
                    html.Div([
                        html.Strong("Training Stage: "),
                        html.Span(tapNodeData['current_stage_actual'])
                    ], className="me-4"),
                ], width='auto'),

                dbc.Col([
                    html.Div([
                        html.Strong("Task: "),
                        html.Span(tapNodeData['task']),
                        html.Div(style = {
                            'display': 'inline-block',
                            'marginLeft': '8px',
                            'width': '12px',
                            'height': '12px',
                            'backgroundColor': task_color,
                            'borderRadius': '50%',
                            'border': '1px solid #ccc',
                            'verticalAlign': 'middle'
                        })
                    ], className="me-4"),
                ], width='auto'),

                dbc.Col([
                    html.Div([
                        html.Strong("Foraging Efficiency: "),
                        html.Span("{:.2f}".format(float(tapNodeData['foraging_eff'])))
                    ], className="me-4"),
                ], width='auto'),
            ], className = "g-0 align-items-center")
        ])
    except Exception as e:
        print(f"Error in display_node_info: {str(e)}")
        return "Error displaying node information"
    
# Highlight callback
@callback(
    Output('dim-reduction-cytoscape', 'elements', allow_duplicate=True),
    [Input('dim-reduction-cytoscape', 'selectedNodeData'),
     State('dim-reduction-cytoscape', 'elements')],
    prevent_initial_call=True
)
def update_node_classes(selected_node_data, elements):
    if not hasattr(update_node_classes, 'previous_node'):
        update_node_classes.previous_node = None
    
    # Debug prints
    print("Selected node data:", selected_node_data)
    
    # Reset network if no node is selected or if clicking the same node
    if not selected_node_data:
        print("Resetting network - no selection")
        update_node_classes.previous_node = None
        return [{**element, 'classes': ''} for element in elements]
    
    # Get the selected node ID and task
    selected_id = selected_node_data[0]['id']
    selected_task = selected_node_data[0]['task']
    print(f"Selected node ID: {selected_id}")
    print(f"Selected task: {selected_task}")
    
    # If clicking the same node, reset
    if selected_id == update_node_classes.previous_node:
        print("Resetting network - same node")
        update_node_classes.previous_node = None
        return [{**element, 'classes': ''} for element in elements]
    
    update_node_classes.previous_node = selected_id
    
    # Find all nodes connected by edges of the same task
    connected_nodes = set()
    connected_edges = set()
    
    # First pass: identify all edges of the same task
    for element in elements:
        if 'source' in element['data']:  # It's an edge
            edge_task = element['data'].get('share_value')  # Changed from color to share_value
            if edge_task == selected_task:
                connected_edges.add(element['data']['id'])
                connected_nodes.add(element['data']['source'])
                connected_nodes.add(element['data']['target'])
    
    print(f"Found {len(connected_nodes)} connected nodes")
    print(f"Found {len(connected_edges)} connected edges")
    
    # Update classes for all elements
    updated_elements = []
    for element in elements:
        new_element = element.copy()
        if 'source' not in element['data']:  # It's a node
            if element['data']['id'] in connected_nodes:
                new_element['classes'] = 'selected'
            else:
                new_element['classes'] = 'faded'
        else:  # It's an edge
            if element['data']['id'] in connected_edges:
                new_element['classes'] = 'selected'
            else:
                new_element['classes'] = 'faded'
        updated_elements.append(new_element)
    
    return updated_elements

server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)
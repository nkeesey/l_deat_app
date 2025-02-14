from dash.dependencies import Input, Output, State, ALL, MATCH
import plotly.express as px
from dash import html
import dash_bootstrap_components as dbc

class UpdateCallbacks:
    def __init__(self, app):
        self.app = app
        self.register_callbacks()
        
    def register_callbacks(self):
        @self.app.callback(
            Output('dim-reduction-cytoscape', 'elements', allow_duplicate=True),
            [Input('dim-reduction-cytoscape', 'selectedNodeData'),
             State('dim-reduction-cytoscape', 'elements')],
            prevent_initial_call=True
        )
        def update_node_classes(selected_node_data, elements):
            if not hasattr(update_node_classes, 'previous_node'):
                update_node_classes.previous_node = None
            
            # Reset network if no node is selected
            if not selected_node_data:
                update_node_classes.previous_node = None
                return [{**element, 'classes': ''} for element in elements]
            
            # Get the selected node ID and task
            selected_id = selected_node_data[0]['id']
            selected_task = selected_node_data[0]['task']
            
            # If clicking the same node, reset
            if selected_id == update_node_classes.previous_node:
                update_node_classes.previous_node = None
                return [{**element, 'classes': ''} for element in elements]
            
            update_node_classes.previous_node = selected_id
            
            # Find connected nodes and edges
            connected_nodes = set()
            connected_edges = set()
            
            for element in elements:
                if 'source' in element['data']:  # It's an edge
                    edge_task = element['data'].get('share_value')
                    if edge_task == selected_task:
                        connected_edges.add(element['data']['id'])
                        connected_nodes.add(element['data']['source'])
                        connected_nodes.add(element['data']['target'])
            
            # Update classes for all elements
            updated_elements = []
            for element in elements:
                new_element = element.copy()
                if 'source' not in element['data']:  # It's a node
                    new_element['classes'] = 'selected' if element['data']['id'] in connected_nodes else 'faded'
                else:  # It's an edge
                    new_element['classes'] = 'selected' if element['data']['id'] in connected_edges else 'faded'
                updated_elements.append(new_element)
            
            return updated_elements

        @self.app.callback(
            Output('node-info', 'children'),
            Input('dim-reduction-cytoscape', 'tapNodeData')
    )
        def display_node_info(tapNodeData):
            if not tapNodeData:
                return "Click a node to see its details"
                
            try:
                # Get color for task
                colors = px.colors.qualitative.Set2
                task_color = colors[hash(tapNodeData['task']) % len(colors)]
                
                # Create info rows based on available data
                info_rows = []
                
                # Add available information
                if 'subject_id' in tapNodeData:
                    info_rows.append(dbc.Col([
                        html.Div([
                            html.Strong("Subject ID: "),
                            html.Span(tapNodeData['subject_id'])
                        ], className="me-4"),
                    ], width='auto'))
                    
                if 'session' in tapNodeData:
                    info_rows.append(dbc.Col([
                        html.Div([
                            html.Strong("Session: "),
                            html.Span(tapNodeData['session'])
                        ], className="me-4"),
                    ], width='auto'))
                    
                if 'current_stage_actual' in tapNodeData:
                    info_rows.append(dbc.Col([
                        html.Div([
                            html.Strong("Training Stage: "),
                            html.Span(tapNodeData['current_stage_actual'])
                        ], className="me-4"),
                    ], width='auto'))
                    
                if 'task' in tapNodeData:
                    info_rows.append(dbc.Col([
                        html.Div([
                            html.Strong("Task: "),
                            html.Span(tapNodeData['task']),
                            html.Div(style={
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
                    ], width='auto'))
                    
                if 'foraging_eff' in tapNodeData:
                    info_rows.append(dbc.Col([
                        html.Div([
                            html.Strong("Foraging Efficiency: "),
                            html.Span("{:.2f}".format(float(tapNodeData['foraging_eff'])))
                        ], className="me-4"),
                    ], width='auto'))
                
                return dbc.Row(info_rows, className="g-0 align-items-center")
                
            except Exception as e:
                print(f"Error in display_node_info: {str(e)}")
                return "Error displaying node information"
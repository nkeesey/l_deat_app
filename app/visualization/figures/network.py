import dash_cytoscape as cyto
import plotly.express as px
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from .base import BaseFigure

class NetworkFigure(BaseFigure):
    def __init__(self, data, stylesheet=None):
        super().__init__(data)
        self.stylesheet = stylesheet or self._create_default_stylesheet()
        
    def create(self):
        nodes, edges = self._prepare_graph(
            df=self.data,
            df_node_info=self.data,
            dim_reduction_results=self.data,
            method='UMAP',  # Change this to match your column names
            connect_by_column='task'
        )
        
        return cyto.Cytoscape(
            id='dim-reduction-cytoscape',  # This ID must match your callbacks
            elements=nodes + edges,
            stylesheet=self.stylesheet,
            style={'width': '100%', 'height': '800px'},
            layout={'name': 'preset'},
            minZoom=0.5,
            maxZoom=10
        )
        
    def _prepare_graph(self, df, df_node_info, dim_reduction_results, 
                  method='umap', max_edges=None, connect_by_column=None):
        """Convert dimensional reduction results to a Cytoscape-compatible graph"""
        # Ensure all dataframes have the same index
        dim_reduction_results = dim_reduction_results.reset_index(drop=True)
        df_node_info = df_node_info.reset_index(drop=True)
        df = df.reset_index(drop=True)
        
        # Verify alignment
        assert len(dim_reduction_results) == len(df_node_info), \
            "Dimension reduction results and node info have different lengths"
        
        # Prepare node coordinates
        x_col = f'{method.upper()}1'
        y_col = f'{method.upper()}2'

        # Normalize coordinates for better visualization
        x_scaler = MinMaxScaler(feature_range=(100, 900))
        y_scaler = MinMaxScaler(feature_range=(100, 900))
        
        dim_reduction_results['x'] = x_scaler.fit_transform(dim_reduction_results[[x_col]])[:,0]
        dim_reduction_results['y'] = y_scaler.fit_transform(dim_reduction_results[[y_col]])[:,0]

        # Prepare nodes
        nodes = []
        for idx, row in dim_reduction_results.iterrows():
            node_info = df_node_info.iloc[idx]
            
            # Create base node data with required fields
            node_data = {
                'id': str(idx),
                'subject_id': str(node_info['subject_id']),
                'session': str(node_info['session']),
                'session_proportion': row['session_proportion'],
                'current_stage_actual': str(node_info['current_stage_actual']),
                'task': str(node_info['task'])
            }
            
            # Optionally add foraging_eff if it exists
            if 'foraging_eff' in node_info:
                node_data['foraging_eff'] = str(node_info['foraging_eff'])
            
            node = {
                'data': node_data,
                'position': {
                    'x': float(row['x']),
                    'y': float(row['y'])
                },
                'classes': f'session-{node_info["session"]}'
            }
            nodes.append(node)

        # Add edges
        edges = []
        if connect_by_column:
            # Create color mapping for all possible combinations 
            colors = px.colors.qualitative.Set2
            all_possible_values = sorted(df[connect_by_column].unique())
            master_color_map = {val: colors[i % len(colors)] 
                              for i, val in enumerate(all_possible_values)}

            # Create edges based on shared values
            value_to_nodes = {}
            for idx, row in df.iterrows():
                value = row[connect_by_column]
                if value not in value_to_nodes:
                    value_to_nodes[value] = []
                value_to_nodes[value].append(str(idx))
            
            # Create edges
            edge_count = 0
            for value, node_ids in value_to_nodes.items():
                if len(node_ids) < 2:
                    continue
                
                for i in range(len(node_ids) - 1):
                    source_id = node_ids[i]
                    target_id = node_ids[i + 1]
                    
                    if source_id != target_id:
                        edge_color = master_color_map[value]
                        edges.append({
                            'data': {
                                'source': source_id,
                                'target': target_id,
                                'weight': 1,
                                'share_value': str(value),
                                'color': edge_color
                            }
                        })
                        edge_count += 1
                    
                    if max_edges and edge_count >= max_edges:
                        break
                
                if max_edges and edge_count >= max_edges:
                    break

        return nodes, edges
    
    def _create_default_stylesheet(self):
        """Create default stylesheet for cytoscape network"""
        return [
            # Base node style
            {
                'selector': 'node',
                'style': {
                    'background-color': 'mapData(session_proportion, 0, 1, #0000FF, #FF0000)',
                    'width': '4px',
                    'height': '4px',
                    'opacity': 0.80
                }
            },
            # Base edge style
            {
                'selector': 'edge',
                'style': {
                    'width': '1px',
                    'line-color': 'data(color)',
                    'opacity': 0.5,
                    'curve-style': 'bezier'
                }
            },
            # Highlighted node style
            {
                'selector': 'node.selected',
                'style': {
                    'opacity': 0.90
                }
            },
            # Highlighted edge style
            {
                'selector': 'edge.selected',
                'style': {
                    'opacity': 0.70
                }
            },
            # Faded node style
            {
                'selector': 'node.faded',
                'style': {
                    'opacity': 0.2
                }
            },
            # Faded edge style
            {
                'selector': 'edge.faded',
                'style': {
                    'opacity': 0.1
                }
            }
        ]

    def update(self, **kwargs):
        """Update the network with new parameters"""
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self.create()
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import networkx as nx
import plotly.express as px

# Set features for processing

experimental_features = [
    'p_reward_sum_mean',
    'p_reward_sum_std',
    'p_reward_sum_median',
    'p_reward_contrast_mean',
    'p_reware_contrast_median',
    'reward_volume_left_mean',
    'reward_volume_right_mean',
    'effective_block_length_mean',
    'effective_block_length_std',
    'effective_block_length_median',
    'effective_block_length_min',
    'effective_block_length_max',
    'duration_gocue_stop_mean',
    'duration_gocue_stop_std',
    'duration_gocue_stop_median',
    'duration_gocue_stop_min',
    'duration_gocue_stop_max',
    'duration_delay_period_mean',
    'duration_delay_period_std',
    'duration_delay_period_median',
    'duration_delay_period_min',
    'duration_delay_period_max',
    'duration_iti_mean',
    'duration_iti_std',
    'duration_iti_median',
    'duration_iti_min',
    'duration_iti_max'
]

performance_features = [
    'total_trials_with_autowater',
    'finished_trials_with_autowater',
    'finished_rate_with_autowater',
    'ignore_rate_with_autowater',
    'autowater_collected',
    'autowater_ignored',
    'total_trials',
    'finished_trials',
    'ignored_trials',
    'finished_rate',
    'ignore_rate',
    'reward_trials',
    'reward_rate',
    'foraging_eff',
    'foraging_eff_random_seed',
    'foraging_performance',
    'foraging_performance_random_seed',
    'bias_naive',
    'early_lick_rate',
    'invalid_lick_ratio',
    'double_dipping_rate_finished_trials',
    'double_dipping_rate_finished_reward_trials',
    'double_dipping_rate_finished_noreward_trials',
    'lick_consistency_mean_finished_trials',
    'lick_consistency_mean_finished_reward_trials',
    'lick_consistency_mean_finished_noreward_trials',
    'reaction_time_median',
    'reaction_time_mean'

]

## Cytoscape functions
def prepare_cyo_graph(df, df_node_info, dim_reduction_results, method='pca', max_edges=None, connect_by_column=None):
    """
    Convert dimensional reduction results to a Cytoscape-compatible graph
    """
    # Ensure all dataframes have the same index
    dim_reduction_results = dim_reduction_results.reset_index(drop=True)
    df_node_info = df_node_info.reset_index(drop=True)
    df = df.reset_index(drop=True)
    
    # Verify alignment
    assert len(dim_reduction_results) == len(df_node_info), "Dimension reduction results and node info have different lengths"
    
    # Prepare node coordinates
    x_col = f'{method.upper()}1'
    y_col = f'{method.upper()}2'

    # Normalize coordinates for better visualization
    x_scaler = MinMaxScaler(feature_range=(100, 900))
    y_scaler = MinMaxScaler(feature_range=(100, 900))
    
    dim_reduction_results['x'] = x_scaler.fit_transform(dim_reduction_results[[x_col]])[:,0]
    dim_reduction_results['y'] = y_scaler.fit_transform(dim_reduction_results[[y_col]])[:,0]

    # Prepare nodes - ensure we create a node for every row
    nodes = []
    for idx, row in dim_reduction_results.iterrows():
        # Get corresponding node info
        node_info = df_node_info.iloc[idx]  # Changed from previous incorrect indexing
        
        node = {
            'data': {
                'id': str(idx),
                'subject_id': str(node_info['subject_id']),  # Fixed indexing
                'session': str(node_info['session']),
                'session_proportion': row['session_proportion'],
                'current_stage_actual': str(node_info['current_stage_actual']),
                'foraging_eff': str(node_info['foraging_eff']),
                'task': str(node_info['task'])
            },
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
        # Create edges based on shared values in connect_by_column

        # Create color mapping for all possible combinations 
        colors = px.colors.qualitative.Set2
        all_possible_values = sorted(df[connect_by_column].unique())
        master_color_map = {val: colors[i % len(colors)] for i, val in enumerate(all_possible_values)}

        # Debugging for master color map
        print('Master color map:')
        for val, color in master_color_map.items():
            print(f'Task: {val} -> Color: {color}')

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
    

def create_cyo_stylesheet():
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
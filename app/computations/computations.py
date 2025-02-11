import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler
from umap.umap_ import UMAP
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
import dash_cytoscape as cyto
import networkx as nx


from app.computations.utils import behavior_utils as bu
from app.computations.utils import ml_utils as ml


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

## Data loading and preprocessing functions

def load_data(filepath='/Users/nickkeesey/projects/l_deat_app/l_deat_app/data/current_2025301.csv'):
    """ Load data from file """
    try:
        df = pd.read_csv(filepath)
        print(f'Loaded {len(df)} rows from {filepath}')
        return df
    except Exception as e:
        print(f'Error loading data: {str(e)}')
        raise

# need to add more processing here (grad level limits, rig filtering, etc.)
def preprocess_data(df, experimental_features=experimental_features, performance_features=performance_features):
    """ Preprocess data """
    df_processed = df.copy()

    df_processed = ml.clean_numeric_features(df_processed, experimental_features + performance_features)

    # Remove rows with NaN values in current_stage_actual column
    df_processed = df_processed.dropna(subset=['current_stage_actual'])

    # Add session column 
    df_processed = bu.add_session_column(df_processed)

    # Add ML-oriented processing
    df_processed = ml.calculate_session_proportion(df_processed)

    return df_processed


def do_umap(df, feature_columns=experimental_features + performance_features, n_components = 2, n_neighbors = 15, min_dist = 0.1, random_state = 42):

    # ensure alignment
    df_reset = df.reset_index(drop=True)

    # get features
    feature_df = df_reset[feature_columns]

    # scale
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(feature_df)
    
    # perform umap
    umap = UMAP(
        n_components = n_components,
        n_neighbors = n_neighbors,
        min_dist = min_dist,
        random_state = random_state
    )

    umap_results = umap.fit_transform(scaled_features)

    # create umap dataframe
    umap_df = pd.DataFrame(
        data = umap_results,
        columns = [f'UMAP{i + 1}' for i in range(n_components)]
    )

    # add metadata
    umap_df['subject_id'] = df_reset['subject_id']
    umap_df['session'] = df_reset['session']
    umap_df['session_proportion'] = df_reset['session_proportion']
    umap_df['current_stage_actual'] = df_reset['current_stage_actual']
    umap_df['task'] = df_reset['task']
    return umap_df
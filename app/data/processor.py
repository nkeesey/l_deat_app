import pandas as pd
from sklearn.preprocessing import StandardScaler
from umap.umap_ import UMAP
from ..utils import MLUtils, BehaviorUtils

class DataProcessor:
    def __init__(self, experimental_features, performance_features):
        self.experimental_features = experimental_features
        self.performance_features = performance_features
        
    def preprocess_data(self, df):
        """Preprocess data"""
        df_processed = df.copy()
        
        # Clean numeric features
        df_processed = MLUtils.clean_numeric_features(
            df_processed, 
            self.experimental_features + self.performance_features
        )
        
        # Remove rows with NaN values in current_stage_actual
        df_processed = df_processed.dropna(subset=['current_stage_actual'])
        
        # Add session column
        df_processed = BehaviorUtils.add_session_column(df_processed)
        
        # Add ML-oriented processing
        df_processed = MLUtils.calculate_session_proportion(df_processed)
        
        return df_processed
        
    def do_umap(self, df, n_components=2, n_neighbors=15, min_dist=0.1, random_state=42):
        """Perform UMAP dimension reduction"""
        # ensure alignment
        df_reset = df.reset_index(drop=True)

        # get features
        feature_df = df_reset[self.experimental_features + self.performance_features]

        # scale
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(feature_df)
        
        # perform umap
        umap = UMAP(
            n_components=n_components,
            n_neighbors=n_neighbors,
            min_dist=min_dist,
            random_state=random_state
        )

        umap_results = umap.fit_transform(scaled_features)

        # create umap dataframe
        umap_df = pd.DataFrame(
            data=umap_results,
            columns=[f'UMAP{i+1}' for i in range(n_components)]
        )

        # add metadata
        umap_df['subject_id'] = df_reset['subject_id']
        umap_df['session'] = df_reset['session']
        umap_df['session_proportion'] = df_reset['session_proportion']
        umap_df['current_stage_actual'] = df_reset['current_stage_actual']
        umap_df['task'] = df_reset['task']
        
        return umap_df
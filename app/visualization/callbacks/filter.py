from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

class FilterCallbacks:
    def __init__(self, app, network_figure):
        self.app = app
        self.network_figure = network_figure
        self.register_callbacks()
        
    def register_callbacks(self):
        @self.app.callback(
            [Output('dim-reduction-plot', 'children'),
             Output('processing-state', 'children')],
            [Input('subject-filter', 'value'),
             Input('stage-filter', 'value'),
             Input('task-filter', 'value'),
             Input('session-range', 'value'),
             Input('n-neighbors-input', 'value'),
             Input('min-dist-input', 'value')]
        )
        def update_dim_reduction_plot(selected_subjects, selected_stages, 
                            selected_tasks, session_range,
                            n_neighbors, min_dist):
            """Update dimension reduction plot based on filters"""
            try:
                # Filter data based on selections
                filtered_df = self.network_figure.data.copy()
                
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
                    
                # Update network figure with filtered data and new parameters
                self.network_figure.data = filtered_df
                updated_figure = self.network_figure.update(
                    n_neighbors=n_neighbors,
                    min_dist=min_dist
                )
                
                return updated_figure, "Processing complete"
            except Exception as e:
                return None, f"Error: {str(e)}"
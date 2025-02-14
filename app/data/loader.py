from aind_analysis_arch_result_access.han_pipeline import get_session_table

class DataLoader:
    def __init__(self, max_rows=11000):
        self.max_rows = max_rows
        
    def load_data(self, load_bpod=False):
        """Load data from session table"""
        try:
            df = get_session_table(if_load_bpod=load_bpod)
            print(f'Loaded {len(df)} rows from session table')
            
            if len(df) > self.max_rows:
                print(f'Limiting data from {len(df)} rows to {self.max_rows} rows')
                df = df.sample(self.max_rows, random_state=42)
                
            return df
        except Exception as e:
            print(f'Error loading data: {str(e)}')
            raise
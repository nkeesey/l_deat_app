import numpy as np
import pandas as pd
from typing import Dict, List, Any
import os

class DataService:
    def __init__(self, csv_path: str):
        """
        Initialize path to csv file
        """
        self.csv_path = csv_path
        self._df = None # Cache the dataframe

    def _load_data(self) -> None:
        """
        Load the data from the csv file
        """
        try:
            self._df = pd.read_csv(self.csv_path)
        except Exception as e:
            raise Exception(f"Error loading data: {str(e)}")
        
    @property
    def df(self) -> pd.DataFrame:
        """ Get dataframe, load if necessary"""
        if self._df is None:
            self._load_data()
        return self._df
    
    def get_column_stats(self, column: str) -> Dict[str, Any]:
        """ Get basic stats for a column ** """
        if column not in self.df.columns:
            raise ValueError(f"Column '{column}' not found in dataset")
        
        stats = {
            'mean': float(self.df[column].mean()) if pd.api.types.is_numeric_dtype(self.df[column]) else None,
            'null_count': int(self.df[column].isnull().sum()),
            'unique_count': int(self.df[column].nunique()),
            'sample_values': self.df[column].dropna().sample(min(10, len(self.df[column])), random_state=42).tolist()
        }
        return stats

    def get_filtered_data(self, filters: Dict[str, Any], page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        """Get filtered and paginated data."""
        filtered_df = self.df.copy()
        
        # Apply filters
        for column, value in filters.items():
            if column in filtered_df.columns:
                filtered_df = filtered_df[filtered_df[column].astype(str).str.contains(str(value), na=False)]
        
        # Calculate pagination
        total_records = len(filtered_df)
        total_pages = (total_records + page_size - 1) // page_size
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        return {
            'data': filtered_df.iloc[start_idx:end_idx].to_dict(orient='records'),
            'total_records': total_records,
            'total_pages': total_pages,
            'current_page': page
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get dataset summary."""
        return {
            'total_rows': len(self.df),
            'columns': list(self.df.columns),
            'memory_usage': self.df.memory_usage(deep=True).sum() / 1024 / 1024,  # MB
            'null_counts': self.df.isnull().sum().to_dict()
        }

# Potential issue below
def check_file_exists(file_path: str) -> bool:
    """Check if a file exists at the given path."""
    csv_path = 'data/comparison_bonsai_df.csv'
    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        return False
    return True

if __name__ == "__main__":
    check_file_exists('data/comparison_bonsai_df.csv')
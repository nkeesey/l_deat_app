from .core import Config, DashServer
from .data import DataLoader, DataProcessor
from .visualization import DashboardLayout, NetworkFigure, FilterCallbacks, UpdateCallbacks

def create_app(config_class=Config):
    # Initialize server
    server = DashServer(config_class)
    app = server.get_app()
    
    # Load and process data
    loader = DataLoader(max_rows=config_class.MAX_ROWS)
    processor = DataProcessor(
        experimental_features=config_class.EXPERIMENTAL_FEATURES,
        performance_features=config_class.PERFORMANCE_FEATURES
    )
    
    # Load and process data
    df = loader.load_data()
    df_processed = processor.preprocess_data(df)
    
    # Create UMAP transformation
    df_umap = processor.do_umap(df_processed)
    
    # Create network figure
    network_figure = NetworkFigure(df_umap)
    
    # Create layout
    app.layout = DashboardLayout(df_processed, network_figure).create()
    
    # Register callbacks
    FilterCallbacks(app, network_figure)
    UpdateCallbacks(app)
    
    return app
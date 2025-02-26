from dash import html
import dash_bootstrap_components as dbc
from .header import Header
from .sidebar import Sidebar

class DashboardLayout:
    def __init__(self, df, network_figure):
        self.df = df
        self.network_figure = network_figure
        
    def create(self):
        return html.Div([
            # Header
            Header.create(),
            
            # Main content
            dbc.Container([
                dbc.Row([
                    # Sidebar
                    Sidebar(self.df).create(),
                    
                    # Main plot area
                    dbc.Col([
                        # Network plot
                        html.Div(
                            self.network_figure.create(),
                            id='dim-reduction-plot'
                        ),
                        
                        # Node info
                        html.Div(id='node-info', className='mt-3')
                    ], width=10)
                ])
            ], fluid=True)
        ])
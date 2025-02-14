import dash_bootstrap_components as dbc
from dash import html

class Header:
    @staticmethod
    def create():
        return dbc.Navbar([
            dbc.Container([
                html.Div([
                    html.H1("Learning Dynamics Exploratory Analysis Tool", 
                        className="mb-0",
                        style={
                            'font-size': '1.0rem',
                            'font-weight': '550',
                            'font-family': '"Segoe UI", Arial, sans-serif',
                            'letter-spacing': '0.5px',
                            'color': '#333'
                        }
                    ),
                ], className="d-flex flex-column")
            ], fluid=True)
        ], 
            dark=False,
            color="light",
            className="mb-4 py-2",
            style={
                'box-shadow': '0 2px 4px rgba(0,0,0,0.1)',
                'background': '#f8f9fa',
                'padding-left': '2rem'
            }
        )
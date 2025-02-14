from dash import Dash
from flask_cors import CORS

class DashServer:
    def __init__(self, config_class):
        self.app = Dash(
            __name__,
            url_base_pathname='/',
            external_stylesheets=[config_class.STYLESHEET],
            suppress_callback_exceptions=True
        )
        self.config = config_class
        CORS(self.app.server)
        self.server = self.app.server
    
    def get_app(self):
        return self.app
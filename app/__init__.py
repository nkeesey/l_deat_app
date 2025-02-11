from flask import Flask
from flask_cors import CORS
from config import Config
from app.dashboard import server as dash_server

def create_app(config_class=Config):
    app = dash_server
    app.config.from_object(config_class)
    CORS(app)  # Enable CORS for all routes

    
    from app.routes import main
    app.register_blueprint(main)
    
    return app
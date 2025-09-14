#!/usr/bin/env python3
"""
Entry point for the CarKeep core API.
"""

from flask import Flask, request
from flask_cors import CORS
from pathlib import Path
import os

def create_api_app(test_config=None):
    """Initialize the core API application."""
    app = Flask(__name__, instance_path=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance'))
    
    # Enable CORS for development with specific settings for Safari
    CORS(app, resources={r"/*": {
        "origins": ["http://localhost:5001", "http://127.0.0.1:5001"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept"],
        "supports_credentials": True,
        "expose_headers": ["Content-Range", "X-Content-Range"]
    }})
    
    # Load configuration directly
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATA_FOLDER=Path(__file__).resolve().parent / 'data',
        DEBUG=True
    )
    
    @app.before_request
    def log_request_info():
        """Log request details for debugging."""
        app.logger.debug('Headers: %s', dict(request.headers))
        app.logger.debug('Body: %s', request.get_data())
    
    # Add a test route
    @app.route('/hello')
    def hello():
        return {'message': 'Hello from the API!'}
    
    # Register API blueprint
    from core.api.routes import api_bp
    app.register_blueprint(api_bp)
    
    return app

app = create_api_app()

if __name__ == '__main__':
    # Ensure all required directories exist
    Path('data/scenarios').mkdir(parents=True, exist_ok=True)
    Path('data/exports').mkdir(parents=True, exist_ok=True)
    Path('data/configs').mkdir(parents=True, exist_ok=True)
    
    app.run(host='localhost', port=5050)
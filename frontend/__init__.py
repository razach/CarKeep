"""
Frontend application module for CarKeep.
Handles UI rendering and user interactions.
"""

from flask import Flask
from pathlib import Path
import os

def create_app(test_config=None):
    """Create and configure the frontend Flask application."""
    app = Flask(__name__, instance_path=os.path.join(os.path.abspath(os.path.dirname(__file__)), '../instance'))
    app.logger.setLevel('DEBUG')

    # Load configuration directly
    app.config.from_mapping(
        SECRET_KEY='dev',
        API_BASE_URL='http://localhost:5050',
        STATIC_FOLDER='static',
        TEMPLATE_FOLDER='templates'
    )
    
    # Initialize API client
    from .utils.api_client import APIClient
    app.api_client = APIClient()
    
    # Register routes
    from .routes import frontend_bp
    app.register_blueprint(frontend_bp)
    
    return app
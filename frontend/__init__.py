"""
Frontend application module for CarKeep.
Handles UI rendering and user interactions.
"""

from flask import Flask
import os

def create_app(test_config=None):
    """Create and configure the frontend Flask application."""
    app = Flask(__name__, instance_path=os.path.join(os.path.abspath(os.path.dirname(__file__)), '../instance'))
    app.logger.setLevel('DEBUG')

    # Base defaults
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        API_BASE_URL=os.environ.get('API_BASE_URL', 'http://localhost:5050'),  # API origin (no trailing /api)
        STATIC_FOLDER='static',
        TEMPLATE_FOLDER='templates',
        DEBUG=os.environ.get('FLASK_DEBUG', '1') == '1'
    )

    # Load instance config if present (overrides defaults)
    try:
        app.config.from_pyfile('config.py', silent=True)
    except Exception:
        pass

    # Finally, environment variables override instance config for deploys
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', app.config.get('SECRET_KEY', 'dev'))
    app.config['API_BASE_URL'] = os.environ.get('API_BASE_URL', app.config.get('API_BASE_URL', 'http://localhost:5050'))
    app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', '1') == '1'
    
    # Initialize API client
    from .utils.api_client import APIClient
    app.api_client = APIClient()
    
    # Register routes
    from .routes import frontend_bp
    app.register_blueprint(frontend_bp)
    
    return app
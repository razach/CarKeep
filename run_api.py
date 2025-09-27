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
    
    # Enable CORS with configurable origins
    allowed_origins_env = os.environ.get('API_ALLOWED_ORIGINS')
    default_origins = [
        "http://localhost:5001",
        "http://127.0.0.1:5001",
        "https://v0.app",
        "https://*.v0.app",
        "http://localhost:3000"  # Common v0 dev port
    ]
    if allowed_origins_env:
        # Comma-separated list of origins
        origins = [o.strip() for o in allowed_origins_env.split(',') if o.strip()]
        default_origins.extend(origins)
    
    # For production, allow all origins temporarily for v0 integration
    if os.environ.get('FLASK_ENV') == 'production':
        cors_origins = "*"  # Allow all for v0 integration
    else:
        cors_origins = default_origins
        
    CORS(app, resources={r"/*": {
        "origins": cors_origins,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept", "X-API-Key"],
        "supports_credentials": True,
        "expose_headers": ["Content-Range", "X-Content-Range"]
    }})
    
    # Load configuration (env overrides)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        DATA_FOLDER=Path(__file__).resolve().parent / 'data',
        DEBUG=os.environ.get('FLASK_DEBUG', '1') == '1'
    )
    
    # Apply security middleware
    from core.api.security import apply_security
    apply_security(app)
    
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
    
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', '5050')))
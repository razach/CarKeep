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
    
    # Enable CORS with specific allowed origins
    allowed_origins_env = os.environ.get('API_ALLOWED_ORIGINS')
    default_origins = [
        "http://localhost:5001",
        "http://127.0.0.1:5001",
        "http://localhost:3000",
        "http://localhost:3001", 
        "https://v0.app",
        "https://v0.dev",
        # v0.app subdomains - common patterns
        "https://chat.v0.app",
        "https://preview.v0.app",
        "https://www.v0.app",
        # Production frontend URL
        "https://carkeep-frontend.onrender.com"
    ]
    
    if allowed_origins_env:
        # Add additional origins from environment
        additional_origins = [o.strip() for o in allowed_origins_env.split(',') if o.strip()]
        default_origins.extend(additional_origins)
        
    CORS(app, resources={r"/*": {
        "origins": default_origins,
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
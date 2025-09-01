"""
Flask application factory for CarKeep web application.
"""

from flask import Flask
from pathlib import Path

def create_app(test_config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    
    # Configure app
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATA_FOLDER=Path(__file__).parent.parent / 'data',
        CORE_FOLDER=Path(__file__).parent.parent / 'core'
    )
    
    if test_config is None:
        # Load the instance config, if it exists
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.update(test_config)
    
    # Ensure the instance folder exists
    try:
        Path(app.instance_path).mkdir(exist_ok=True)
    except OSError:
        pass
    
    # Register blueprints
    from .routes import main_bp
    app.register_blueprint(main_bp)
    
    return app

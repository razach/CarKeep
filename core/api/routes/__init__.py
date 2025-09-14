"""
API routes initialization.
"""

from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/test')
def test_endpoint():
    """Test endpoint to verify API is working."""
    return {'status': 'ok', 'message': 'API is working'}

# Import routes
from .scenarios import *  # All route handlers are imported here

# Register routes
# The route decorators in scenarios.py will automatically register with api_bp
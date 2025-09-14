"""
API utility functions for CarKeep core functionality.
"""

from functools import wraps
from flask import jsonify, request
import jwt

def require_auth(f):
    """Decorator to require authentication for API endpoints."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'success': False, 'error': 'No authorization header'}), 401
            
        try:
            # TODO: Implement proper JWT validation
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 401
            
    return decorated

def validate_request(schema):
    """Decorator to validate request data against a schema."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                data = request.get_json()
                schema.validate(data)
                return f(*args, **kwargs)
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 400
        return decorated
    return decorator
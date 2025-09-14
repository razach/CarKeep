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
    """Decorator to validate request data against a schema.

    Supports two modes:
    - Dict schema: { 'required': ['field1', 'field2', ...] }
    - Object schema: object with a .validate(data) method (e.g., marshmallow)
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                data = request.get_json(silent=True)
                if data is None:
                    return jsonify({'success': False, 'error': 'Invalid or missing JSON payload'}), 400

                # Dict-based simple schema support
                if isinstance(schema, dict):
                    required = schema.get('required', [])
                    missing = [key for key in required if key not in data or data.get(key) in (None, '')]
                    if missing:
                        return jsonify({'success': False, 'error': f"Missing required fields: {', '.join(missing)}"}), 400
                else:
                    # Fallback to calling .validate if available
                    validate_fn = getattr(schema, 'validate', None)
                    if callable(validate_fn):
                        validate_fn(data)

                return f(*args, **kwargs)
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 400
        return decorated
    return decorator
"""
Basic API security utilities for CarKeep.
"""
from functools import wraps
from flask import request, jsonify, current_app
from datetime import datetime, timedelta
import os


# Simple in-memory rate limiting (for basic protection)
request_counts = {}
RATE_LIMIT_REQUESTS = 100  # requests per minute
RATE_LIMIT_WINDOW = 60  # seconds


def get_client_ip():
    """Get client IP address, handling proxies."""
    if request.headers.get('X-Forwarded-For'):
        return request.headers['X-Forwarded-For'].split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers['X-Real-IP']
    else:
        return request.remote_addr


def rate_limit(f):
    """Simple rate limiting decorator."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = get_client_ip()
        now = datetime.now()
        
        # Clean old entries
        cutoff = now - timedelta(seconds=RATE_LIMIT_WINDOW)
        request_counts[client_ip] = [
            req_time for req_time in request_counts.get(client_ip, [])
            if req_time > cutoff
        ]
        
        # Check rate limit
        if len(request_counts.get(client_ip, [])) >= RATE_LIMIT_REQUESTS:
            return jsonify({
                'error': 'Rate limit exceeded',
                'message': f'Maximum {RATE_LIMIT_REQUESTS} requests per minute'
            }), 429
        
        # Add current request
        if client_ip not in request_counts:
            request_counts[client_ip] = []
        request_counts[client_ip].append(now)
        
        return f(*args, **kwargs)
    
    return decorated_function


def check_api_key(f):
    """Optional API key checking decorator."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip API key check if not configured
        required_api_key = os.environ.get('CARKEEP_API_KEY')
        if not required_api_key:
            return f(*args, **kwargs)
        
        # Check for API key in header
        provided_key = request.headers.get('X-API-Key') or request.headers.get('Authorization')
        if provided_key and provided_key.replace('Bearer ', '') == required_api_key:
            return f(*args, **kwargs)
        
        return jsonify({
            'error': 'Invalid or missing API key',
            'message': 'Provide API key in X-API-Key header'
        }), 401
    
    return decorated_function


def apply_security(app):
    """Apply security middleware to Flask app."""
    
    @app.before_request
    def security_headers():
        """Add basic security headers."""
        pass  # Headers are handled by CORS for now
    
    @app.after_request
    def after_request(response):
        """Add security headers to response."""
        # Basic security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Cache control for API responses
        if request.path.startswith('/api/'):
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        
        return response
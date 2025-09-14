"""
API client for communicating with the core API.

Configuration:
- API_BASE_URL should be set to the API origin (e.g., https://api.example.com) with no trailing /api.
- Endpoints passed to this client should include the /api prefix (e.g., '/api/scenarios').
"""

import requests
from flask import current_app

class APIError(Exception):
    """Custom exception for API errors."""
    pass

class APIClient:
    """Client for making requests to the core API."""
    
    def __init__(self, base_url=None, timeout=30):
        """Initialize the API client."""
        self.base_url = base_url
        self.timeout = timeout
        
    def _get_base_url(self):
        """Get the base URL from app config if not set."""
        return self.base_url or current_app.config['API_BASE_URL']
        
    def _make_request(self, method, endpoint, **kwargs):
        """Make a request to the API."""
        url = f"{self._get_base_url()}/{endpoint.lstrip('/')}"
        
        try:
            response = requests.request(
                method, 
                url, 
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise APIError(f"API request failed: {str(e)}")
    
    def get(self, endpoint, params=None):
        """Make a GET request."""
        return self._make_request('GET', endpoint, params=params)
    
    def post(self, endpoint, data=None, json=None):
        """Make a POST request."""
        return self._make_request('POST', endpoint, data=data, json=json)
    
    def put(self, endpoint, data=None, json=None):
        """Make a PUT request."""
        return self._make_request('PUT', endpoint, data=data, json=json)
    
    def delete(self, endpoint):
        """Make a DELETE request."""
        return self._make_request('DELETE', endpoint)
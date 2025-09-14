#!/usr/bin/env python3
"""
Entry point for the CarKeep frontend application.
"""

from frontend import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='localhost', port=5001)
    
    # Run the application
    app.run(debug=True, port=5000)

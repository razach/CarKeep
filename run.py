#!/usr/bin/env python3
"""
Entry point for the CarKeep frontend application.
"""

from frontend import create_app

app = create_app()

if __name__ == '__main__':
    # Run the frontend on port 5001
    app.run(host='localhost', port=5001, debug=True)

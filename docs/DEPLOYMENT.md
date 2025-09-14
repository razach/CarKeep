# Deployment Guide

This project follows the “Keep It Simple” approach with server-rendered Flask + Jinja and incremental htmx. For hosting, we’ll use two services on Render.com:

Option B (Recommended): Separate Frontend and API on Render.

## Overview

- Frontend: Flask app serving HTML (Jinja templates) at https://your-frontend.onrender.com
- API: Flask app serving JSON under /api at https://your-api.onrender.com
- Browser -> Frontend -> (server-side) API pattern: All browser requests go to the Frontend. The Frontend calls the API using the server-side API client (no browser-to-API calls). This keeps CORS simple and avoids mixed-content/auth pitfalls.

## Render Setup

1) API Service (Flask)
- Root: repository root
- Start command (basic): python run_api.py
- Environment variables:
  - SECRET_KEY=change-me
  - FLASK_DEBUG=0
  - (Optional) API_ALLOWED_ORIGINS=https://your-frontend.onrender.com
- Networking:
  - Ensure CORS allows your Frontend origin (update run_api.py CORS list).
  - HTTPS is provided by Render; use https URLs.

2) Frontend Service (Flask)
- Root: repository root
- Start command (basic): python run.py
- Environment variables:
  - SECRET_KEY=change-me
  - FLASK_DEBUG=0
  - API_BASE_URL=https://your-api.onrender.com  # Note: no trailing /api

## Key Constraints and Best Practices

- API_BASE_URL must be absolute and HTTPS (e.g., https://your-api.onrender.com) and should NOT include the trailing /api. Frontend routes include the /api prefix when calling the backend (e.g., client.get('/api/scenarios')).
- CORS: The API should allow the Frontend’s Render origin. If you later add additional domains, add them to allowed origins.
- Same-origin UX: All htmx/browser interactions should target Frontend routes that render HTML or trigger server-side API calls. Do not call the API directly from the browser to avoid CORS/auth issues.
- Static assets: Served by the Frontend service under /static.
- Error handling: Standardize API error payloads (JSON) and surface human-friendly messages in templates.

## Optional Hardening (Future)

- Use Gunicorn for production serving (e.g., gunicorn -w 2 -k gthread run:app)
- Make CORS origins environment-driven (e.g., API_ALLOWED_ORIGINS) in run_api.py
- Authentication: Prefer token-based (Bearer) if you add accounts; cross-origin cookies require SameSite=None; Secure.

## Troubleshooting

- Mixed content errors: Ensure API_BASE_URL uses https.
- CORS blocked: Confirm API CORS origins include your frontend URL and methods/headers align with requests.
- 404s on /api: Verify API_BASE_URL includes /api suffix and the API blueprint is mounted at /api.

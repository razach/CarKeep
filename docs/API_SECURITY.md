# CarKeep API Security

## Current Security Measures

### 1. Rate Limiting
- **Limit**: 100 requests per minute per IP address
- **Response**: HTTP 429 (Too Many Requests) when exceeded
- **Implementation**: In-memory tracking (resets on server restart)

### 2. CORS Protection
- **Allowed Origins**: 
  - `localhost:5001` (local frontend development)
  - `https://v0.app` and `https://*.v0.app` (v0 builder)
  - `localhost:3000` (common v0 dev port)
  - Additional origins via `API_ALLOWED_ORIGINS` environment variable
- **Headers**: Restricts which domains can call the API

### 3. Security Headers
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY` 
- `X-XSS-Protection: 1; mode=block`
- Cache control for API responses

### 4. Optional API Key (Not Currently Required)
- Set `CARKEEP_API_KEY` environment variable to enable
- Include key in `X-API-Key` header or `Authorization: Bearer <key>`
- Currently disabled to allow easy v0 integration

## Recommendations for Production

### Enable API Key Protection
```bash
# On Render, set environment variable:
CARKEEP_API_KEY=your-secret-api-key-here
```

### Monitor Usage
- Rate limiting provides basic protection
- Consider upgrading to Redis-based rate limiting for production
- Add logging for suspicious activity

### Additional Security (Future)
- JWT-based authentication for user-specific data
- Request signing for sensitive operations
- IP whitelisting for admin operations

## For v0 Integration

**Current**: No API key required - works out of the box
**Production**: Add API key to headers when enabled

```javascript
// If API key is enabled
fetch('https://carkeep.onrender.com/api/scenarios', {
  headers: {
    'X-API-Key': 'your-api-key'
  }
})
```
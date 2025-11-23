# Nginx Configuration

This directory contains the Nginx server configuration for Padel Watcher.

## Files

- `default.conf` - Main server configuration with routing rules

## Configuration Overview

### HTTP Server (Default)
- Listens on port 80
- Proxies `/api/*` to backend container
- Proxies all other traffic to frontend container
- Rate limiting enabled

### HTTPS Server (Optional)
- Uncomment the HTTPS server block in `default.conf` to enable
- Requires SSL certificates in `/nginx/ssl/`
- Includes security headers
- HTTP/2 support

## Customization

### Change Domain
Replace `yourdomain.com` with your actual domain in the HTTPS server block.

### Adjust Rate Limits
Edit rate limit zones in `default.conf`:
- `api_limit`: 10 requests/second for general API
- `login_limit`: 5 requests/minute for login endpoint

### Add Custom Routes
Add location blocks in the server section:
```nginx
location /custom {
    proxy_pass http://custom-service:port;
}
```

## Testing Configuration

```bash
# Test nginx configuration
docker-compose exec nginx nginx -t

# Reload configuration
docker-compose exec nginx nginx -s reload
```

## Security Headers

The following security headers are enabled:
- `X-Frame-Options: SAMEORIGIN`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Content-Security-Policy` (when HTTPS is enabled)

## Performance

- Gzip compression enabled for text assets
- Static asset caching (1 year for immutable files)
- HTTP/2 support (when HTTPS enabled)
- Connection pooling and keep-alive

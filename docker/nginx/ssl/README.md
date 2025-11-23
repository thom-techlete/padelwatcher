# SSL Certificates Directory

Place your SSL certificates in this directory for HTTPS support.

## Using Let's Encrypt with Certbot

1. **Install Certbot** on your VPS:
```bash
sudo apt-get update
sudo apt-get install certbot
```

2. **Generate certificates** (with nginx running):
```bash
sudo certbot certonly --webroot -w /var/www/certbot -d yourdomain.com -d www.yourdomain.com
```

3. **Copy certificates** to this directory:
```bash
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ./nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ./nginx/ssl/
```

4. **Update nginx configuration**:
- Uncomment the HTTPS server block in `nginx/conf.d/default.conf`
- Replace `yourdomain.com` with your actual domain
- Restart nginx: `docker-compose restart nginx`

## Certificate Files

- `fullchain.pem` - Full certificate chain
- `privkey.pem` - Private key

## Auto-renewal

Set up a cron job for automatic renewal:
```bash
0 0 * * * certbot renew --quiet && docker-compose restart nginx
```

## Security Notes

- Never commit certificate files to git
- Certificates are already in `.gitignore`
- Keep private keys secure with proper file permissions (600)

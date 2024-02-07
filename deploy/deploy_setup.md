# Deploy Setup

### Build Docker Container Image (optional)

    docker build . -t kevincoakley/osn-discovery-api-server:<git_hash>

### Add cred.yml for the osn-discovery-api Service

```yaml
site-a.com:
  access_key: XXX
  secret_key: YYY
site-b.com:
  access_key: XXX
  secret_key: YYY
```

### Generate Intial SSL Certificates

    docker run --name certbot -p 80:80 -v "$(pwd)/certbot/conf:/etc/letsencrypt" -v "$(pwd)/certbot/www:/var/www/certbot" certbot/certbot certonly --standalone --email <email> -d <hostname> --rsa-key-size 4096 --agree-tos --no-eff-email --non-interactive

### Deploy or Update the Stack

    docker compose up -d

### Delete the Stack

    docker compose down
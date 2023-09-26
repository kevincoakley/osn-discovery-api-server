# Deploy Setup

### Build Docker Container Image

    docker build . -t kevincoakley/osd-discovery-api:<git_hash>

### Tag the osd-discovery-api Image

    docker image tag <image_id> kevincoakley/osd-discovery-api:latest

### Add cred.yml

### Generate Intial SSL Certificates

    docker run --name certbot -p 80:80 -v "$(pwd)/certbot/conf:/etc/letsencrypt" -v "$(pwd)/certbot/www:/var/www/certbot" certbot/certbot certonly --standalone --email <email> -d <hostname> --rsa-key-size 4096 --agree-tos --no-eff-email --non-interactive

### Deploy the Stack

    docker compose up -d

### Delete the Stack

    docker compose down
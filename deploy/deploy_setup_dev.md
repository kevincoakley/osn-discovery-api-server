# Deploy Setup (Development)

### Build Docker API Container Image (optional)

    docker build . -t kevincoakley/osn-discovery-api-server:<git_hash>

### Build Docker WEBUI Container Image (optional)

    docker build . -t kevincoakley/osn-discovery-webui:<git_hash>

### Overwrite the Production Nginx Conf File with the Development Nginx Conf File

    mv nginx/sites-enabled/osn-explorer.conf-dev nginx/sites-enabled/osn-explorer.conf

### Update docker-compose.yml with Local Development Docker Container Images (optional)

### Deploy or Update the Stack

    docker compose up -d

### Delete the Stack

    docker compose down
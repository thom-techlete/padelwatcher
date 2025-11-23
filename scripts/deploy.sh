#!/bin/bash

# Padel Watcher - Production Deployment Script
# This script helps deploy Padel Watcher to a VPS

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "================================================"
echo "   Padel Watcher - Production Deployment"
echo "================================================"
echo -e "${NC}"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠ No .env file found. Creating from .env.example...${NC}"
    cp .env.example .env
    echo -e "${RED}✗ Please edit .env file with your production values before continuing!${NC}"
    echo -e "${YELLOW}  Required fields:${NC}"
    echo "  - POSTGRES_PASSWORD"
    echo "  - SECRET_KEY"
    echo "  - GMAIL_AUTH_CODE"
    echo "  - GMAIL_SENDER_EMAIL"
    echo "  - FRONTEND_BASE_URL"
    echo "  - CORS_ORIGINS"
    exit 1
fi

# Validate required environment variables
echo -e "${YELLOW}Checking environment variables...${NC}"
source .env

REQUIRED_VARS=(
    "POSTGRES_PASSWORD"
    "SECRET_KEY"
    "GMAIL_AUTH_CODE"
    "GMAIL_SENDER_EMAIL"
)

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ] || [[ "${!var}" == *"change-me"* ]] || [[ "${!var}" == *"your-"* ]]; then
        echo -e "${RED}✗ $var is not set or contains default value${NC}"
        echo -e "${YELLOW}  Please update .env file with production values${NC}"
        exit 1
    fi
done

echo -e "${GREEN}✓ Environment variables validated${NC}"

# Check Docker installation
echo -e "${YELLOW}Checking Docker installation...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker is not installed${NC}"
    echo "Please install Docker: https://docs.docker.com/engine/install/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}✗ Docker Compose is not installed${NC}"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✓ Docker is installed${NC}"

# Create required directories
echo -e "${YELLOW}Creating required directories...${NC}"
mkdir -p nginx/ssl nginx/logs backups backend/data

echo -e "${GREEN}✓ Directories created${NC}"

# Build and start containers
echo -e "${YELLOW}Building Docker images...${NC}"
docker-compose build

echo -e "${GREEN}✓ Images built successfully${NC}"

echo -e "${YELLOW}Starting containers...${NC}"
docker-compose up -d

echo -e "${GREEN}✓ Containers started${NC}"

# Wait for database to be ready
echo -e "${YELLOW}Waiting for database to be ready...${NC}"
sleep 10

# Run database migrations
echo -e "${YELLOW}Running database migrations...${NC}"
docker-compose exec -T backend alembic upgrade head

echo -e "${GREEN}✓ Database migrations completed${NC}"

# Show container status
echo -e "${YELLOW}Container status:${NC}"
docker-compose ps

echo -e "${GREEN}"
echo "================================================"
echo "   ✓ Deployment completed successfully!"
echo "================================================"
echo -e "${NC}"

echo -e "${BLUE}Next steps:${NC}"
echo "1. Create an admin user:"
echo -e "   ${YELLOW}docker-compose exec backend python scripts/create_admin.py${NC}"
echo ""
echo "2. Configure SSL certificates (recommended):"
echo -e "   ${YELLOW}See nginx/ssl/README.md for instructions${NC}"
echo ""
echo "3. Set up automated backups:"
echo -e "   ${YELLOW}crontab -e${NC}"
echo -e "   ${YELLOW}0 2 * * * /path/to/padelwatcher/scripts/backup.sh${NC}"
echo ""
echo "4. Monitor logs:"
echo -e "   ${YELLOW}docker-compose logs -f${NC}"
echo ""
echo -e "${GREEN}Your application should be accessible at:${NC}"
echo -e "   ${BLUE}http://$(hostname -I | awk '{print $1}')${NC}"
echo ""

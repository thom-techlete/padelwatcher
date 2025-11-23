#!/bin/bash

# Padel Watcher - Health Check Script
# Verifies all services are running correctly

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "Padel Watcher - Health Check"
echo "============================="
echo ""

# Check if containers are running
echo -n "Checking containers... "
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ Containers not running${NC}"
    docker-compose ps
    exit 1
fi

# Check database
echo -n "Checking database... "
if docker-compose exec -T db pg_isready -U padelwatcher > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ Database not ready${NC}"
    exit 1
fi

# Check backend health endpoint
echo -n "Checking backend API... "
if curl -sf http://localhost/api/health > /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ Backend health check failed${NC}"
    exit 1
fi

# Check frontend
echo -n "Checking frontend... "
if curl -sf http://localhost/health > /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ Frontend health check failed${NC}"
    exit 1
fi

# Check disk space
echo -n "Checking disk space... "
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    echo -e "${GREEN}✓ ($DISK_USAGE% used)${NC}"
elif [ "$DISK_USAGE" -lt 90 ]; then
    echo -e "${YELLOW}⚠ ($DISK_USAGE% used)${NC}"
else
    echo -e "${RED}✗ ($DISK_USAGE% used - critically low)${NC}"
fi

# Check Docker disk usage
echo -n "Checking Docker disk usage... "
docker system df --format "table {{.Type}}\t{{.Size}}" | tail -n +2

echo ""
echo -e "${GREEN}All health checks passed!${NC}"

#!/bin/bash
# Script to run the Padel Watcher API

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Padel Watcher API...${NC}"

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "${YELLOW}Warning: Virtual environment not activated${NC}"
    echo "Consider running: source .venv/bin/activate"
fi

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}Warning: .env file not found${NC}"
    echo "Creating from example..."
    cp backend/.env.example backend/.env
fi

# Change to backend directory
cd backend

# Check if database exists
if [ ! -f "../data/padel.db" ]; then
    echo -e "${YELLOW}Database not found. Running migrations...${NC}"
    alembic upgrade head
fi

# Start the API
echo -e "${GREEN}API starting on http://localhost:5000${NC}"
python -m app.api

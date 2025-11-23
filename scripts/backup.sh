#!/bin/bash

# Padel Watcher - Database Backup Script
# This script creates automated PostgreSQL backups

set -e

# Configuration
BACKUP_DIR="$(dirname "$0")/../backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
CONTAINER_NAME="padelwatcher-db"
DB_NAME="${POSTGRES_DB:-padelwatcher}"
DB_USER="${POSTGRES_USER:-padelwatcher}"
RETENTION_DAYS=7

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Check if container is running
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    echo -e "${RED}Error: Database container '$CONTAINER_NAME' is not running${NC}"
    exit 1
fi

echo -e "${YELLOW}Starting database backup...${NC}"

# Create backup
BACKUP_FILE="$BACKUP_DIR/backup_${TIMESTAMP}.sql"
if docker exec "$CONTAINER_NAME" pg_dump -U "$DB_USER" "$DB_NAME" > "$BACKUP_FILE"; then
    echo -e "${GREEN}✓ Database dumped successfully${NC}"
else
    echo -e "${RED}✗ Failed to dump database${NC}"
    exit 1
fi

# Compress backup
if gzip "$BACKUP_FILE"; then
    echo -e "${GREEN}✓ Backup compressed: backup_${TIMESTAMP}.sql.gz${NC}"
else
    echo -e "${RED}✗ Failed to compress backup${NC}"
    exit 1
fi

# Get backup size
BACKUP_SIZE=$(du -h "$BACKUP_FILE.gz" | cut -f1)
echo -e "${GREEN}Backup size: ${BACKUP_SIZE}${NC}"

# Clean old backups
OLD_BACKUPS=$(find "$BACKUP_DIR" -name "backup_*.sql.gz" -mtime +$RETENTION_DAYS)
if [ -n "$OLD_BACKUPS" ]; then
    echo -e "${YELLOW}Removing backups older than $RETENTION_DAYS days...${NC}"
    find "$BACKUP_DIR" -name "backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete
    echo -e "${GREEN}✓ Old backups removed${NC}"
fi

# Count remaining backups
BACKUP_COUNT=$(find "$BACKUP_DIR" -name "backup_*.sql.gz" | wc -l)
echo -e "${GREEN}Total backups: $BACKUP_COUNT${NC}"

echo -e "${GREEN}✓ Backup completed successfully!${NC}"

#!/bin/bash

# Make scripts executable
chmod +x scripts/*.sh

# Create necessary directories
mkdir -p nginx/ssl nginx/logs backups backend/data

echo "✓ Scripts are now executable"
echo "✓ Required directories created"

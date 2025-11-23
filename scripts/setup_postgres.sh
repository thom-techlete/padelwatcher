#!/bin/bash
# Setup script to create PostgreSQL database for Padelwatcher

echo "🔧 Setting up PostgreSQL database for Padelwatcher..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Default values
POSTGRES_HOST=${POSTGRES_HOST:-localhost}
POSTGRES_PORT=${POSTGRES_PORT:-5432}
POSTGRES_USER=${POSTGRES_USER:-padelwatcher}
POSTGRES_DB=${POSTGRES_DB:-padelwatcher}

echo "📊 Database details:"
echo "  Host: $POSTGRES_HOST"
echo "  Port: $POSTGRES_PORT"
echo "  Database: $POSTGRES_DB"
echo "  User: $POSTGRES_USER"

# Create database and user (run as postgres superuser)
echo ""
echo "Creating database and user..."
echo "You may need to enter your PostgreSQL admin password (postgres user)"

# Create user and database
sudo -u postgres psql << EOF
-- Create user if not exists
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = '$POSTGRES_USER') THEN
        CREATE USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD';
    END IF;
END
\$\$;

-- Create database if not exists
SELECT 'CREATE DATABASE $POSTGRES_DB OWNER $POSTGRES_USER'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$POSTGRES_DB')\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO $POSTGRES_USER;

\c $POSTGRES_DB

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO $POSTGRES_USER;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $POSTGRES_USER;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $POSTGRES_USER;

EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Database setup completed successfully!"
    echo ""
    echo "Next steps:"
    echo "  1. Install Python dependencies: pip install -r backend/requirements.txt"
    echo "  2. Run Alembic migrations: cd backend && alembic upgrade head"
    echo "  3. Migrate SQLite data: python backend/scripts/migrate_sqlite_to_postgres.py"
else
    echo ""
    echo "❌ Database setup failed!"
    exit 1
fi

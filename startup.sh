#!/bin/bash

# John & Eniola Financial Consultancy - Startup Script
# This script sets up and runs the Flask application

echo "================================"
echo "John & Eniola Consultancy Setup"
echo "================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt -q

# Check if .env exists
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  .env file not found!"
    echo "Please create .env file with your configuration:"
    echo ""
    echo "SECRET_KEY=your-secret-key"
    echo "DB_USER=root"
    echo "DB_PASSWORD="
    echo "DB_HOST=localhost"
    echo "DB_PORT=3306"
    echo "DB_NAME=john_eniola_consultancy"
    echo "MAIL_SERVER=smtp.gmail.com"
    echo "MAIL_PORT=587"
    echo "MAIL_USERNAME=your-email@gmail.com"
    echo "MAIL_PASSWORD=your-app-password"
    echo ""
    exit 1
fi

# Initialize database
echo ""
echo "Initializing database..."
python init_db.py

# Run the application
echo ""
echo "================================"
echo "Starting Flask Application"
echo "================================"
echo ""
echo "✓ Application is running at: http://localhost:5000"
echo "✓ Admin dashboard: http://localhost:5000/admin"
echo "✓ Username: admin"
echo "✓ Password: admin123"
echo ""
echo "⚠️  IMPORTANT: Change the admin password immediately!"
echo ""

python app.py

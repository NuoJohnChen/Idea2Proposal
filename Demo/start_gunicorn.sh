#!/bin/bash

# AI Research Proposal Evaluation System - Gunicorn Startup Script
# This script sets up and starts the application with Gunicorn

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting AI Research Proposal Evaluation System with Gunicorn${NC}"

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo -e "${RED}❌ Error: app.py not found. Please run this script from the Demo directory.${NC}"
    exit 1
fi

# Create logs directory if it doesn't exist
echo -e "${YELLOW}📁 Creating logs directory...${NC}"
mkdir -p logs

# Check if gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    echo -e "${YELLOW}📦 Installing gunicorn...${NC}"
    pip install gunicorn==21.2.0
fi

# Check if configuration file exists
if [ ! -f "gunicorn.conf.py" ]; then
    echo -e "${RED}❌ Error: gunicorn.conf.py not found.${NC}"
    exit 1
fi

# Check if wsgi.py exists
if [ ! -f "wsgi.py" ]; then
    echo -e "${RED}❌ Error: wsgi.py not found.${NC}"
    exit 1
fi

# Set environment variables
export FLASK_ENV=production

# Start gunicorn
echo -e "${GREEN}🎯 Starting Gunicorn server...${NC}"
echo -e "${YELLOW}📍 Server will be available at: http://localhost:4090${NC}"
echo -e "${YELLOW}📊 Logs will be written to: logs/ directory${NC}"
echo -e "${YELLOW}🛑 Press Ctrl+C to stop the server${NC}"
echo ""

# Start gunicorn with configuration
exec gunicorn --config gunicorn.conf.py wsgi:app

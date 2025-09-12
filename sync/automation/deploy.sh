#!/bin/bash
# WILLOW Sync System Deployment Script
# Automated deployment for HVSCMA CMA operations

set -e

echo "Starting WILLOW Sync System Deployment..."
echo "Timestamp: $(date)"

# Configuration
REPO_URL="https://github.com/HVSCMA/hvscma-cmas.git"
SYNC_DIR="/opt/willow-sync"
VENV_DIR="$SYNC_DIR/venv"
LOG_DIR="/var/log/willow"

# Create directories
sudo mkdir -p $SYNC_DIR
sudo mkdir -p $LOG_DIR
sudo chown $USER:$USER $SYNC_DIR
sudo chown $USER:$USER $LOG_DIR

# Clone or update repository
if [ -d "$SYNC_DIR/.git" ]; then
    echo "Updating existing repository..."
    cd $SYNC_DIR
    git pull origin main
else
    echo "Cloning repository..."
    git clone $REPO_URL $SYNC_DIR
fi

# Set up Python virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv $VENV_DIR
fi

# Activate virtual environment and install dependencies
source $VENV_DIR/bin/activate
pip install --upgrade pip
pip install PyGithub requests jsonschema

# Create systemd service file
sudo tee /etc/systemd/system/willow-sync.service > /dev/null <<EOF
[Unit]
Description=WILLOW Automated Sync System
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$SYNC_DIR/sync/automation
Environment=PATH=$VENV_DIR/bin
ExecStart=$VENV_DIR/bin/python willow_sync_controller.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable willow-sync.service

echo "WILLOW Sync System deployment completed successfully!"
echo "To start the service: sudo systemctl start willow-sync"
echo "To check status: sudo systemctl status willow-sync"
echo "Logs available at: $LOG_DIR/"

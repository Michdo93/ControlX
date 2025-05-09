#!/bin/bash

# Make sure the script is run with root privileges
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run with root privileges." 
    exit 1
fi

# Current directory and username
CURRENT_DIR=$(pwd)
USER=$(whoami)

# Ensure SQLite is installed
echo "Checking for SQLite..."
if ! command -v sqlite3 &> /dev/null; then
    echo "SQLite is not installed. Installing..."
    apt update && apt install -y sqlite3 libsqlite3-dev
else
    echo "SQLite is already installed."
fi

# Ensure that requirements.txt exists
if [ ! -f "$CURRENT_DIR/requirements.txt" ]; then
    echo "requirements.txt not found. Please make sure the file exists."
    exit 1
fi

# Install Python dependencies
echo "Installing Python dependencies..."
python3 -m pip install -r "$CURRENT_DIR/requirements.txt"

python3 create_db.py

# Create the systemd service file
SERVICE_FILE="/etc/systemd/system/controlx.service"

echo "Creating systemd service file..."

cat <<EOF > $SERVICE_FILE
[Unit]
Description=ControlX Web Application
After=network.target

[Service]
User=$USER
Group=$USER
WorkingDirectory=$CURRENT_DIR
ExecStart=/usr/bin/python3 $CURRENT_DIR/app.py
Restart=always
Environment="FLASK_ENV=production"
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
EOF

# Set permissions for the service file
chmod 644 $SERVICE_FILE

# Enable and start the service
echo "Enabling and starting the ControlX service..."
systemctl daemon-reload
systemctl enable controlx.service
systemctl start controlx.service

echo "Installation completed."

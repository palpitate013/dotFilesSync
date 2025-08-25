#!/usr/bin/env bash
set -e

# Variables
SCRIPT_NAME="file-sync.py"
INSTALL_DIR="/usr/local/bin"
INSTALL_PATH="$INSTALL_DIR/$SCRIPT_NAME"
SERVICE_NAME="file-sync.service"
SYSTEMD_PATH="/etc/systemd/system/$SERVICE_NAME"
USER=$(whoami)

# Check for Python 3
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] Python3 not found. Please install it first."
    exit 1
fi

# Install watchdog if needed
if ! python3 -c "import watchdog" &>/dev/null; then
    echo "[INFO] Installing watchdog Python package..."
    python3 -m pip install --user watchdog
fi

# Copy script to /usr/local/bin
echo "[INFO] Installing $SCRIPT_NAME to $INSTALL_PATH..."
sudo mkdir -p "$INSTALL_DIR"
sudo cp "$SCRIPT_NAME" "$INSTALL_PATH"
sudo chmod +x "$INSTALL_PATH"

# Create systemd service
echo "[INFO] Creating systemd service..."
sudo tee "$SYSTEMD_PATH" > /dev/null <<EOF
[Unit]
Description=File Sync Watcher
After=network.target

[Service]
ExecStart=/usr/bin/env python3 $INSTALL_PATH
Restart=always
User=$USER
WorkingDirectory=$HOME
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
echo "[INFO] Enabling and starting systemd service..."
sudo systemctl daemon-reload
sudo systemctl enable --now "$SERVICE_NAME"

echo "[DONE] File sync watcher installed and running!"
echo "You can check logs with: sudo journalctl -u $SERVICE_NAME -f"

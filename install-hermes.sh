#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SERVICE_NAME="xiaoai-cloud"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

echo "=== XiaoAI Cloud Plugin Installer ==="

# Check Node.js version
NODE_VERSION=$(node -v 2>/dev/null | sed 's/v//' | cut -d. -f1)
if [ -z "$NODE_VERSION" ] || [ "$NODE_VERSION" -lt 22 ]; then
    echo "Error: Node.js 22+ required. Current: $(node -v 2>/dev/null || echo 'not installed')"
    exit 1
fi
echo "✓ Node.js $(node -v)"

# Build
echo "Building..."
cd "$SCRIPT_DIR"
npm install --production=false
npm run build
echo "✓ Build complete"

# Create config directory
CONFIG_DIR="$HOME/.hermes/xiaoai-cloud"
mkdir -p "$CONFIG_DIR"
echo "✓ Config directory: $CONFIG_DIR"

# Install systemd service
if [ -d /etc/systemd/system ]; then
    read -p "Install systemd service? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp "$SCRIPT_DIR/xiaoai-cloud.service" "$SERVICE_FILE"
        systemctl daemon-reload
        echo "✓ Service installed: $SERVICE_NAME"
        echo "  Start with: sudo systemctl start $SERVICE_NAME"
        echo "  Enable on boot: sudo systemctl enable $SERVICE_NAME"
    fi
fi

echo ""
echo "=== Installation Complete ==="
echo ""
echo "Next steps:"
echo "1. Create config: $CONFIG_DIR/config.json"
echo "2. Start service: npm start (or sudo systemctl start $SERVICE_NAME)"
echo "3. Open console: http://localhost:17890/console"
echo "4. Login with Xiaomi account"

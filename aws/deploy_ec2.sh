#!/bin/bash
# ==============================================================================
# RoadSense EC2 Automated Deployment Script (Ubuntu 24.04 LTS)
# Installs system dependencies, Python runtime, Nginx, builds Web App,
# and configures systemd daemon for 24/7 uptime.
# ==============================================================================

set -e

echo "🚀 [1/6] Updating system packages & configuring swap..."
sudo apt-get update -y
sudo apt-get install -y python3-pip python3-venv nginx git curl jq libpq-dev

# Create 2GB swap file to prevent OOM kills on t3.micro (1GB RAM) during npm build
if [ ! -f /swapfile ]; then
    echo "💾 Creating 2GB Swap Memory..."
    sudo fallocate -l 2G /swapfile || sudo dd if=/dev/zero of=/swapfile bs=1M count=2048
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
fi

# Install Node.js (v20 LTS) for building the React Web Admin portal
if ! command -v node &> /dev/null; then
    echo "📦 [2/6] Installing Node.js LTS..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

# Set project working directory
APP_DIR="/var/www/roadsense"
sudo mkdir -p $APP_DIR
sudo chown -R $USER:$USER $APP_DIR

echo "📂 [3/6] Setting up Python virtual environment..."
cd $APP_DIR/lib/backend
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

echo "🌐 [4/6] Building React Admin Web Portal..."
cd $APP_DIR/web-admin
npm install
rm -rf dist
npm run build
sudo mkdir -p /var/www/roadsense-admin
sudo cp -r dist/* /var/www/roadsense-admin/
sudo mkdir -p /var/www/roadsense-admin/dist
sudo cp -r dist/* /var/www/roadsense-admin/dist/
sudo chown -R www-data:www-data /var/www/roadsense-admin
sudo chmod -R 755 /var/www/roadsense-admin

echo "⚙️ [5/6] Configuring Nginx Reverse Proxy..."
sudo cp $APP_DIR/aws/nginx.conf /etc/nginx/sites-available/roadsense
sudo ln -sf /etc/nginx/sites-available/roadsense /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

echo "🛡️ [6/6] Creating Systemd Service for Gunicorn Backend..."
sudo tee /etc/systemd/system/roadsense.service > /dev/null <<EOF
[Unit]
Description=RoadSense Cloud REST API Engine
After=network.target

[Service]
User=$USER
WorkingDirectory=$APP_DIR/lib/backend
Environment="PATH=$APP_DIR/lib/backend/venv/bin"
Environment="FLASK_ENV=production"
Environment="RUNNING_IN_AWS=true"
Environment="PORT=6969"
ExecStart=$APP_DIR/lib/backend/venv/bin/gunicorn --workers 2 --bind 127.0.0.1:6969 "backend_main:create_app()"
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable roadsense
sudo systemctl restart roadsense

echo "✅ RoadSense Cloud Platform successfully deployed on EC2!"
echo "📍 Access your Web Admin Portal at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"

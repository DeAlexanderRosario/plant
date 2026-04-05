#!/bin/bash
echo "[EdenScope] Starting Raspberry Pi 3B Optimization & Installation..."

# 1. INCREASE SWAP SPACE (Crucial for 1GB RAM Pi 3B)
echo "[EdenScope] Increasing swap space to 2GB to prevent installation crashes..."
sudo dphys-swapfile swapoff
sudo sed -i 's/CONF_SWAPSIZE=.*/CONF_SWAPSIZE=2048/' /etc/dphys-swapfile
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
echo "[EdenScope] Swap space increased to 2GB."

# 2. PYTHON VERSION CHECK
# Python 3.13 is often too new for pre-built AI wheels on Raspberry Pi.
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "[EdenScope] Detected Python version: $PYTHON_VERSION"

if [[ "$PYTHON_VERSION" == "3.12" || "$PYTHON_VERSION" == "3.13" ]]; then
    echo "--------------------------------------------------------------------------------"
    echo "WARNING: Python $PYTHON_VERSION is very new for ARM architecture (RPi)."
    echo "Some packages (like torch) might take several HOURS to compile."
    echo "We HIGHLY recommend using Raspberry Pi OS Bullseye (Python 3.9) or Bookworm (3.11)."
    echo "--------------------------------------------------------------------------------"
    sleep 5
fi

# 3. INSTALL SYSTEM DEPENDENCIES
echo "[EdenScope] Installing system dependencies for OpenCV/AI..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv libatlas-base-dev libhdf5-dev libhdf5-serial-dev libqt5gui5 libqt5test5 libqt5core5a v4l-utils

# 4. SETUP VIRTUAL ENVIRONMENT
echo "[EdenScope] Refreshing Python virtual environment..."
rm -rf venv
python3 -m venv venv
source venv/bin/activate

# 5. INSTALL PYTHON PACKAGES
echo "[EdenScope] Installing optimized dependencies from requirements.txt..."
pip install --upgrade pip
# Ensure we have the latest RPi.GPIO or compatible lpgio
pip install --no-cache-dir rpi-lgpio || pip install --no-cache-dir RPi.GPIO
pip install --no-cache-dir -r requirements.txt

# 6. SETUP SYSTEM SERVICE
echo "[EdenScope] Updating systemd auto-run service..."
CURRENT_USER=$(whoami)
WORKING_DIR=$(pwd)

# Create/Update service file dynamically
cat <<EOF > plant_protector.service
[Unit]
Description=EdenScope Drone Payload Service
After=network.target

[Service]
Type=simple
WorkingDirectory=$WORKING_DIR
ExecStart=$WORKING_DIR/venv/bin/python pi_server.py
Restart=always
RestartSec=5
User=$CURRENT_USER

[Install]
WantedBy=multi-user.target
EOF

sudo cp plant_protector.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable plant_protector.service
sudo systemctl restart plant_protector.service

echo "[EdenScope] --------------------------------------------------------"
echo "[EdenScope] Installation Complete!"
echo "[EdenScope] UI access: http://$(hostname -I | awk '{print $1}'):5000"
echo "[EdenScope] View logs: sudo journalctl -u plant_protector -f"
echo "[EdenScope] --------------------------------------------------------"

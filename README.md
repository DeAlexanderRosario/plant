# EdenScope | Autonomous Plant Protection System

**EdenScope** is a professional-grade, Raspberry Pi-powered payload designed for automated agricultural monitoring and protection. Using AI-driven optics, it identifies plant anomalies and triggers an automated irrigation system in real-time.

---

## 🚀 Key Features

- **AI-Driven Optics**: Real-time YOLOv8 disease and anomaly detection.
- **Automated Irrigation**: Precision GPIO-controlled relay for targeted spraying.
- **Professional Dashboard**: Clean, industrial-grade monitoring interface.
- **Real-time Telemetry**: Detailed system data on detections, status, and input source.
- **Dynamic Configuration**: Adjust AI confidence and hardware timings via the UI without rebooting.

---

## 🛠️ Technical Stack

- **Core Engine**: Python 3.x
- **Inference**: YOLOv8 (PyTorch/TFLite)
- **Web Interface**: Flask / Modern Inter CSS
- **Hardware Control**: RPi.GPIO (Asynchronous)

---

## 📦 1. Headless Hardware Setup
*No monitor, keyboard, or mouse (HID) required.*

1.  **Flash OS**: Use [Raspberry Pi Imager](https://www.raspberrypi.com/software/).
2.  **Configure (Ctrl+Shift+X)**:
    - **General**: Set Hostname (`edenscope`), Username, Password, and Wi-Fi.
    - **Services**: **Enable SSH** (use password authentication).
3.  **Insert & Boot**: Power on the Pi. It will automatically connect to your network.

---

## 💻 2. Deployment

### Connect via SSH
```bash
ssh pi@edenscope.local
```

### Install Software
```bash
cd ~/raspberry_pi_payload
chmod +x install_pi.sh
./install_pi.sh
```

### Auto-start at Boot (Background Service)
To ensure **EdenScope** starts immediately whenever the Pi is powered on:
```bash
sudo cp plant_protector.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable plant_protector
sudo systemctl start plant_protector
```

---

## 🌐 3. Access & Control

Open your browser and navigate to:
**`http://edenscope.local:5000`**

### Configuration Parameters
- **AI Confidence**: Set the detection sensitivity (0.1 to 0.9).
- **Sprinkler Duration**: Control how long the relay stays active.
- **Recharge Interval**: Set the safety cooldown between activation cycles.

---

## 🔌 Hardware Wiring (BCM Layout)
- **BCM 17 (Pin 11)**: Relay Control Module.
- **Camera Port**: Pi Camera or any USB-C/USB Optic.

---

© 2026 EdenScope Systems. All rights reserved.

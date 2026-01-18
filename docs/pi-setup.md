# InkFrame Raspberry Pi Setup Guide

## Prerequisites
- Raspberry Pi Zero 2 W
- Waveshare 7.5" e-ink display HAT
- MicroSD card (32GB+)
- Wi-Fi credentials
- InkFrame project repository

## Step 1: Flash Operating System
1. Download and open Raspberry Pi Imager
2. Select **Raspberry Pi Zero 2 W** as device
3. Select **Raspberry Pi OS (64-bit)** as OS
4. Click gear icon ⚙️ for settings:
   - Hostname: `inkframe`
   - Username: `pi`
   - Password: `<your-password>`
   - Configure Wi-Fi (SSID, password, country: AU)
   - Locale: Australia/Sydney, keyboard: us
   - Enable SSH with password authentication
5. Write to SD card
6. Insert SD card into Pi and power on
7. Wait 2 minutes for first boot

## Step 2: Connect via SSH
```bash
ssh pi@inkframe.local
```

## Step 3: Enable SPI Interface
```bash
sudo raspi-config
```
- Navigate to: `Interface Options` → `SPI` → `Yes`
- Exit and reboot:
```bash
sudo reboot
```

## Step 4: Install System Dependencies
SSH back in after reboot:
```bash
ssh pi@inkframe.local
```

Install required system packages:
```bash
sudo apt update
sudo apt install -y git python3-pip python3-venv swig liblgpio-dev python3-lgpio
```

## Step 5: Clone Project Repository
```bash
cd ~
git clone <your-github-repo-url> inkframe
cd inkframe
```

## Step 6: Transfer Secrets File
From your **Windows terminal** (not SSH):
```bash
scp C:\path\to\your\inkframe\config\secrets.yaml pi@inkframe.local:/home/pi/inkframe/config/
```

## Step 7: Set Up Python Environment
Back in SSH session:
```bash
cd ~/inkframe
python3 -m venv venv
source venv/bin/activate
```

## Step 8: Install Python Dependencies
```bash
pip install pillow requests pyyaml spidev RPi.GPIO gpiozero lgpio
```

## Step 9: Install Waveshare Display Library
```bash
git clone https://github.com/waveshare/e-Paper.git
cd e-Paper/RaspberryPi_JetsonNano/python
pip install .
cd ~/inkframe
```

## Step 10: Verify Installation
Test that all libraries load correctly:
```bash
python -c "from waveshare_epd import epd7in5_V2; print('Success')"
```

Should print `Success` with no errors.

## Step 11: Wire Display HAT
1. Power off Pi: `sudo shutdown -h now`
2. Carefully align Waveshare HAT with all 40 GPIO pins
3. Press firmly and evenly until seated
4. Power on Pi

## Step 12: Test Display
```bash
cd ~/inkframe
source venv/bin/activate
python -m src.system.cli refresh
```

Weather should appear on e-ink display!

## Step 13: Install Systemd Service (Optional - for automation)
```bash
sudo cp services/inkframe.service /etc/systemd/system/
sudo cp services/inkframe.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable inkframe.timer
sudo systemctl start inkframe.timer
```

## Common Issues
- **Import errors**: Make sure venv is activated (`source venv/bin/activate`)
- **GPIO errors**: Verify SPI is enabled in raspi-config
- **Display not updating**: Check HAT is firmly seated on all pins
- **Network errors**: Verify secrets.yaml has correct API key

## Useful Commands
```bash
# Force manual refresh
python -m src.system.cli refresh

# Check refresh status
python -m src.system.cli status

# Check timer status
sudo systemctl status inkframe.timer

# View logs
tail -f logs/app.log

# Stop automation
sudo systemctl stop inkframe.timer

# Start automation
sudo systemctl start inkframe.timer
```
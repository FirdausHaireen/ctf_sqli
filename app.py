from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# === INIT DB ON STARTUP ===
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        is_admin INTEGER DEFAULT 0
    )''')

    # Add two users: one normal, one admin
    c.execute("INSERT INTO users (username, password, is_admin) VALUES ('user', 'userpass', 0)")
    c.execute("INSERT INTO users (username, password, is_admin) VALUES ('admin', 'supersecret', 1)")
    conn.commit()
    conn.close()

if not os.path.exists("users.db"):
    init_db()

@app.route("/")
def index():
    return jsonify({"message": "Welcome to the API. POST /login with JSON."})

@app.route("/login", methods=["POST"])
def login():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    # Basic WAF (can be bypassed)
    if any(x in username.lower() for x in ["--", ";", " or ", " and ", "=", "=="]):
        return jsonify({"error": "WAF triggered"}), 403

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    query = f"SELECT username, is_admin FROM users WHERE username = '{username}' AND password = '{password}'"
    print("Executing query:", query)
    c.execute(query)
    result = c.fetchone()
    conn.close()

    if result:
        user, is_admin = result
        if is_admin:
            with open("flag.txt") as f:
                flag = f.read().strip()
            return jsonify({"message": f"Welcome admin! Here is your flag: {flag}"})
        return jsonify({"message": f"Welcome {user}, but no flag for you."})
    return jsonify({"error": "Invalid credentials"}), 401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

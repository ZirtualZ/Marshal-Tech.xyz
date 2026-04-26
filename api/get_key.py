# api/get_key.py
from flask import Blueprint, request, jsonify
import sqlite3
import hashlib

get_key_api = Blueprint("get_key_api", __name__, url_prefix="/api/get_key")
DB_FILE = "users.db"

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

@get_key_api.route("", methods=["POST"])
def get_key():
    data = request.json or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("SELECT password_hash, api_key, max_uses, used FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "User not found"}), 404

    db_password_hash, api_key, max_uses, used = row

    if db_password_hash != hash_password(password):
        return jsonify({"error": "Invalid password"}), 401

    if used >= max_uses:
        return jsonify({"error": "API key usage limit reached"}), 403

    return jsonify({"api_key": api_key})

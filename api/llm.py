# api/llm.py
import requests
import traceback
from flask import Blueprint, request, jsonify
import sqlite3

llm_api = Blueprint("llm_api", __name__, url_prefix="/api/llm")
DB_FILE = "users.db"

@llm_api.route("", methods=["POST"])
def ask_llm():
    try:
        api_key = request.headers.get("x-api-key")
        if not api_key:
            return jsonify({"response": "Missing API key"}), 401

        # Check API key
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT max_uses, used FROM users WHERE api_key=?", (api_key,))
        row = c.fetchone()

        if not row:
            conn.close()
            return jsonify({"response": "Invalid or expired API key"}), 401

        max_uses, used = row
        if used >= max_uses:
            conn.close()
            return jsonify({"response": "API key usage limit reached"}), 403

        # Increment usage
        c.execute("UPDATE users SET used = used + 1 WHERE api_key=?", (api_key,))
        conn.commit()
        conn.close()

        data = request.json or {}
        user_prompt = data.get("prompt", "").strip()

        if not user_prompt:
            return jsonify({"response": "No prompt provided"}), 400

        # Use custom system prompt from client, with safe default
        system_prompt = data.get("system_prompt", "").strip()
        if not system_prompt:
            system_prompt = "You are Marshal, a chill laid-back guy. Reply casually and naturally like a normal person on Discord. Keep replies short."

        full_prompt = f"{system_prompt}\n\nUser: {user_prompt}\nYou:"

        # Call Ollama
        r = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.1:8b",      # Make sure this model is pulled
                "prompt": full_prompt,
                "stream": False
            },
            timeout=60
        )

        if r.status_code != 200:
            return jsonify({"response": f"Ollama error {r.status_code}"}), 502

        response_text = r.json().get("response", "No response from model").strip()
        return jsonify({"response": response_text})

    except Exception as e:
        error_details = traceback.format_exc()
        print("=== LLM ENDPOINT ERROR ===")
        print(error_details)
        print("=========================")
        return jsonify({"response": "Server error, try again later"}), 500

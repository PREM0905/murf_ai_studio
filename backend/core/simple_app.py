from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
CORS(app)

@app.route("/text", methods=["POST"])
def text_handler():
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({"ok": False, "error": "No message"}), 400
        
        reply = f"You said: {message}"
        
        return jsonify({
            "ok": True,
            "message": message,
            "reply": reply
        })
        
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/test", methods=["GET"])
def test():
    return jsonify({"status": "Server running"})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
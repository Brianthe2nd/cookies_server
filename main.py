from flask import Flask, request, jsonify
import time
import threading

app = Flask(__name__)

COOKIE_FILES = ["b159.txt", "b603.txt"]

cookie_state = {
    f: {"in_use": False, "last_released": 0}
    for f in COOKIE_FILES
}

lock = threading.Lock()
COOLDOWN = 120


@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "message": "Server is running"})


@app.route("/start", methods=["POST"])
def start():
    with lock:
        now = time.time()
        for f, state in cookie_state.items():
            if not state["in_use"] and (now - state["last_released"]) > COOLDOWN:
                state["in_use"] = True
                return jsonify({"cookie_file": f})

        return jsonify({"cookie_file": None})


@app.route("/end", methods=["POST"])
def end():
    data = request.get_json()
    cookie_file = data.get("cookie_file")

    if cookie_file not in cookie_state:
        return jsonify({"error": "Invalid cookie file"}), 400

    with lock:
        cookie_state[cookie_file]["in_use"] = False
        cookie_state[cookie_file]["last_released"] = time.time()

    return jsonify({"message": f"{cookie_file} released"})


@app.route("/status", methods=["GET"])
def status():
    return jsonify(cookie_state)


@app.route("/reset", methods=["GET"])
def reset():
    """Reset all cookies so they are free immediately (ignores cooldown)"""
    with lock:
        for f in cookie_state:
            cookie_state[f]["in_use"] = False
            cookie_state[f]["last_released"] = 0
    return jsonify({"message": "All cookies reset"})


if __name__ == "__main__":
    app.run(host="::", port=5000)

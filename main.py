from flask import Flask, request, jsonify
import time
import threading

app = Flask(__name__)

COOKIE_FILES = ["b159.txt", "b603.txt"]

cookie_state = {
    f: {"in_use": False, "last_released": 0, "by": None}
    for f in COOKIE_FILES
}

lock = threading.Lock()
COOLDOWN = 120


@app.route("/ping", methods=["GET"])
def ping():
    ip = request.remote_addr
    print(f"[PING] Received ping from {ip}")
    return jsonify({"status": "ok", "message": "Server is running"})


@app.route("/start", methods=["POST"])
def start():
    ip = request.remote_addr
    print(f"[START] Request received from {ip}")

    with lock:
        now = time.time()
        for f, state in cookie_state.items():
            if not state["in_use"] and (now - state["last_released"]) > COOLDOWN:
                state["in_use"] = True
                state["by"] = ip
                print(f"[START] Assigned {f} to {ip}")
                return jsonify({"cookie_file": f})

        print(f"[START] No available cookies for {ip}")
        return jsonify({"cookie_file": None})


@app.route("/end", methods=["POST"])
def end():
    ip = request.remote_addr
    data = request.get_json()
    cookie_file = data.get("cookie_file")
    print(f"[END] Request from {ip} to release {cookie_file}")

    if cookie_file not in cookie_state:
        print(f"[END] Invalid cookie file {cookie_file} from {ip}")
        return jsonify({"error": "Invalid cookie file"}), 400

    with lock:
        cookie_state[cookie_file]["in_use"] = False
        cookie_state[cookie_file]["last_released"] = time.time()
        cookie_state[cookie_file]["by"] = ip
        print(f"[END] {cookie_file} released by {ip}")

    return jsonify({"message": f"{cookie_file} released"})


@app.route("/status", methods=["GET"])
def status():
    ip = request.remote_addr
    print(f"[STATUS] Request from {ip}")
    return jsonify(cookie_state)


@app.route("/reset", methods=["GET"])
def reset():
    ip = request.remote_addr
    print(f"[RESET] Reset request from {ip}")

    with lock:
        for f in cookie_state:
            cookie_state[f]["in_use"] = False
            cookie_state[f]["last_released"] = 0
            cookie_state[f]["by"] = None
    print(f"[RESET] All cookies reset by {ip}")
    return jsonify({"message": "All cookies reset"})


if __name__ == "__main__":
    app.run(host="::", port=5000)

from flask import Flask, request, jsonify, Response
import time
import threading
import logging
import os
from drop import sync_archive_to_dropbox


app = Flask(__name__)

# --- Logging Setup ---
LOG_FILE = "server.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

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
    logger.info(f"[PING] Received ping from {ip}")
    return jsonify({"status": "ok", "message": "Server is running"})


@app.route("/start", methods=["POST"])
def start():
    ip = request.remote_addr
    logger.info(f"[START] Request received from {ip}")
    

    with lock:
        now = time.time()
        for f, state in cookie_state.items():
            if not state["in_use"] and (now - state["last_released"]) > COOLDOWN:
                state["in_use"] = True
                state["by"] = ip
                logger.info(f"[START] Assigned {f} to {ip}")
                return jsonify({"cookie_file": f})

        logger.info(f"[START] No available cookies for {ip}")
        return jsonify({"cookie_file": None})


@app.route("/end", methods=["POST"])
def end():
    ip = request.remote_addr
    data = request.get_json()
    cookie_file = data.get("cookie_file")
    logger.info(f"[END] Request from {ip} to release {cookie_file}")

    if cookie_file not in cookie_state:
        logger.warning(f"[END] Invalid cookie file {cookie_file} from {ip}")
        return jsonify({"error": "Invalid cookie file"}), 400

    with lock:
        current_holder = cookie_state[cookie_file]["by"]

        # Check if the same IP that reserved it is trying to release it
        if current_holder != ip:
            logger.warning(
                f"[END] Unauthorized release attempt: {ip} tried to release {cookie_file}, "
                f"but it is held by {current_holder}"
            )
            return jsonify({"error": "You are not the owner of this cookie"}), 403

        cookie_state[cookie_file]["in_use"] = False
        cookie_state[cookie_file]["last_released"] = time.time()
        cookie_state[cookie_file]["by"] = ip
        logger.info(f"[END] {cookie_file} released by {ip}")

    return jsonify({"message": f"{cookie_file} released"})


@app.route("/status", methods=["GET"])
def status():
    ip = request.remote_addr
    logger.info(f"[STATUS] Request from {ip}")
    return jsonify(cookie_state)


@app.route("/reset", methods=["GET"])
def reset():
    ip = request.remote_addr
    logger.info(f"[RESET] Reset request from {ip}")

    with lock:
        for f in cookie_state:
            cookie_state[f]["in_use"] = False
            cookie_state[f]["last_released"] = 0
            cookie_state[f]["by"] = None
    logger.info(f"[RESET] All cookies reset by {ip}")
    return jsonify({"message": "All cookies reset"})


@app.route("/logs", methods=["GET"])
def get_logs():
    ip = request.remote_addr
    logger.info(f"[LOGS] Logs requested by {ip}")

    if not os.path.exists(LOG_FILE):
        return jsonify({"error": "Log file not found"}), 404

    # Return the log file content as plain text
    with open(LOG_FILE, "r") as f:
        logs = f.read()

    return Response(logs, mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="::", port=5000)

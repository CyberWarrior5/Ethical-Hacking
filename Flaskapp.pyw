import sys
import os
import logging
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import base64
from mss import mss
import threading
import time
from waitress import serve
from PIL import Image
import io
import traceback

# Define the path for the log directory and file
log_dir = os.path.expanduser("~/ScreenRecorder")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, "flaskapp.log")

# Set up logging
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

try:
    # Log system information
    logging.info(f"Python version: {sys.version}")
    logging.info(f"Python executable: {sys.executable}")
    logging.info(f"Current working directory: {os.getcwd()}")
    logging.info(f"Log directory: {log_dir}")

    # Get the directory of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the path to the templates directory
    templates_dir = os.path.join(
        script_dir, os.path.expanduser("~/ScreenRecorder")
    )  # Update with your templates directory path

    # Change the working directory to the script's directory
    os.chdir(script_dir)
    logging.info(f"Changed working directory to: {os.getcwd()}")

    # Set up Flask app
    app = Flask(__name__, template_folder=templates_dir)
    socketio = SocketIO(app, cors_allowed_origins="*")

    # Global variables
    current_monitor = 0
    monitor_count = 0

    def get_monitor_count():
        with mss() as sct:
            return len(sct.monitors) - 1

    def capture_screen():
        global current_monitor, monitor_count
        with mss() as sct:
            while True:
                try:
                    monitor = sct.monitors[current_monitor + 1]
                    logging.debug(f"Capturing monitor: {current_monitor + 1}")
                    screenshot = sct.grab(monitor)
                    img = Image.frombytes(
                        "RGB", screenshot.size, screenshot.bgra, "raw", "BGRX"
                    )
                    buffer = io.BytesIO()
                    img.save(buffer, format="JPEG")
                    image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
                    logging.debug(f"Captured image size: {len(image_base64)}")
                    socketio.emit("screen_update", {"image": image_base64})
                    time.sleep(0.1)
                except Exception as e:
                    logging.error(f"Error in capture_screen: {str(e)}")
                    logging.error(f"Traceback: {traceback.format_exc()}")

    @app.route("/")
    def index():
        global monitor_count
        monitor_count = get_monitor_count()
        return render_template("interface.html")  # Ensure this path is correct

    @socketio.on("connect")
    def on_connect():
        logging.info("Client connected")

    @socketio.on("switch_monitor")
    def switch_monitor(data):
        global current_monitor
        monitor = int(data["monitor"])
        if 0 <= monitor < monitor_count:
            current_monitor = monitor
            logging.info(f"Switched to monitor {current_monitor}")
        else:
            logging.error(f"Invalid monitor number: {monitor}")

    @app.route("/get_monitor_count")
    def get_monitor_count_route():
        global monitor_count
        monitor_count = get_monitor_count()
        return jsonify({"count": monitor_count})

    if __name__ == "__main__":
        logging.info("Starting Flask app with Waitress")
        threading.Thread(target=capture_screen, daemon=True).start()
        serve(
            app, host="0.0.0.0", port=5000
        )  # Make the app accessible on all network interfaces

except Exception as e:
    logging.critical(f"Critical error: {str(e)}")
    logging.critical(f"Traceback: {traceback.format_exc()}")

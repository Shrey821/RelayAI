#!/usr/bin/env python3
"""
Universal Memory Schema (UMS) - One-Click Launcher
Starts the backend server and opens the web application.
"""

import sys
import os
import webbrowser
import threading
import time

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from server.app import start_server

PORT = 8000
HOST = "127.0.0.1"
URL = f"http://{HOST}:{PORT}"

def open_browser():
    time.sleep(1.0)
    print(f"\n🚀 Opening UMS Web Application at {URL} ...")
    try:
        webbrowser.open(URL)
    except Exception:
        pass

if __name__ == "__main__":
    print("""
    ===============================================================
       _   _ __  __ ____    _   _       _                         _ 
      | | | |  \\/  / ___|  | | | |_ __ (_)_   _____ _ __ ___  __ _| |
      | | | | |\\/| \\___ \\  | | | | '_ \\| \\ \\ / / _ \\ '__/ __|/ _` | |
      | |_| | |  | |___) | | |_| | | | | |\\ V /  __/ |  \\__ \\ (_| | |
       \\___/|_|  |_|____/   \\___/|_| |_|_| \\_/ \\___|_|  |___/\\__,_|_|
                       Universal Memory Schema v1.0.0
    ===============================================================
    """)
    print("Starting zero-dependency local server...")
    threading.Thread(target=open_browser, daemon=True).start()
    try:
        start_server(port=PORT, host=HOST)
    except KeyboardInterrupt:
        print("\nUMS Server shut down cleanly.")

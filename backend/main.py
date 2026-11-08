
import json
import os
import subprocess
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import quote_plus
from datetime import datetime

HOST = "127.0.0.1"
PORT = 8765

# Set this to your actual Netlify website URL later.
ALLOWED_ORIGIN = os.environ.get("JARVIS_ORIGIN", "")


def allowed_origin(origin):
    return (
        origin in ("http://localhost:8888", "http://127.0.0.1:8888")
        or (ALLOWED_ORIGIN and origin == ALLOWED_ORIGIN)
    )
from pathlib import Path

def open_installed_app(app_name):
    apps = {
        "discord": ["discord"],
        "roblox": ["roblox", "roblox player"],
        "chrome": ["chrome", "google chrome"],
        "riot client": ["riot client"],
    }

    aliases = apps.get(app_name)

    if not aliases:
        return "I don't have that app registered yet."

    folders = [
        Path(os.environ["APPDATA"]) / "Microsoft/Windows/Start Menu/Programs",
        Path(os.environ["PROGRAMDATA"]) / "Microsoft/Windows/Start Menu/Programs"
    ]

    for folder in folders:
        if folder.exists():
            for shortcut in folder.rglob("*.lnk"):
                if shortcut.stem.lower() in aliases:
                    os.startfile(str(shortcut))
                    return "Opening " + app_name.title() + "."

    return "I couldn't find " + app_name.title() + "."

def run_command(command):
    command = command.lower().strip()

    if command in ("status", "hello"):
        return "JARVIS backend is online and ready."

    if command == "time":
        return "The current time is " + datetime.now().strftime("%I:%M %p")

    if command == "date":
        return "Today is " + datetime.now().strftime("%A, %d %B %Y")

    # Website launcher
    websites = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "chatgpt": "https://chatgpt.com",
        "github": "https://github.com",
        "crunchyroll": "https://www.crunchyroll.com",
        "spotify": "https://open.spotify.com",
        "netflix": "https://www.netflix.com",
        "gmail": "https://mail.google.com"
    }

    for phrase in ("open ", "launch ", "visit ", "go to "):
        if command.startswith(phrase):
            site = command[len(phrase):].strip()

            if site in websites:
                webbrowser.open(websites[site])
                return "Opening " + site.title() + "."
    # Launch installed apps
    for phrase in ("open ", "launch ", "start ", "run "):
        if command.startswith(phrase):
            app_name = command[len(phrase):].strip()

            if app_name in ("notepad", "calculator", "explorer"):
                break

            return open_installed_app(app_name)
    
    if command == "open notepad":
        subprocess.Popen(["notepad.exe"])
        return "Opening Notepad."

    if command == "open calculator":
        subprocess.Popen(["calc.exe"])
        return "Opening Calculator."

    if command == "open explorer":
        subprocess.Popen(["explorer.exe"])
        return "Opening File Explorer."

    if command.startswith("search "):
        query = command[7:].strip()
        if not query:
            return "Please provide something to search for."

        webbrowser.open(
            "https://www.google.com/search?q=" + quote_plus(query)
        )
        return "Searching Google for " + query

    return "I don't recognize that command yet."


class JarvisHandler(BaseHTTPRequestHandler):

    def send_json(self, status, data):
        body = json.dumps(data).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))

        origin = self.headers.get("Origin", "")
        if allowed_origin(origin):
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")

        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        origin = self.headers.get("Origin", "")

        if not allowed_origin(origin):
            self.send_json(403, {"error": "Origin not allowed"})
            return

        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Vary", "Origin")
        self.end_headers()

    def do_GET(self):
        if self.path == "/health":
            self.send_json(200, {"status": "online", "assistant": "JARVIS"})
        else:
            self.send_json(404, {"error": "Endpoint not found"})

    def do_POST(self):
        origin = self.headers.get("Origin", "")

        if not allowed_origin(origin):
            self.send_json(403, {"error": "Origin not allowed"})
            return

        if self.path != "/command":
            self.send_json(404, {"error": "Endpoint not found"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))

            if length <= 0 or length > 4096:
                self.send_json(400, {"error": "Invalid request size"})
                return

            data = json.loads(self.rfile.read(length).decode("utf-8"))
            command = data.get("command", "")

            if not isinstance(command, str) or len(command) > 200:
                self.send_json(400, {"error": "Invalid command"})
                return

            result = run_command(command)
            self.send_json(200, {"reply": result})

        except (ValueError, json.JSONDecodeError):
            self.send_json(400, {"error": "Invalid JSON"})
        except Exception:
            self.send_json(500, {"error": "Command failed"})

    def log_message(self, format, *args):
        print("[JARVIS]", format % args)


if __name__ == "__main__":
    server = HTTPServer((HOST, PORT), JarvisHandler)

    print("--------------------------------")
    print("       J.A.R.V.I.S. ONLINE")
    print("--------------------------------")
    print(f"Local server: http://{HOST}:{PORT}")
    print("Press CTRL+C to stop JARVIS.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nJARVIS shutting down...")
        server.server_close()

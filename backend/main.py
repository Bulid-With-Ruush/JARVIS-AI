
import json
import subprocess
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import quote_plus

HOST = "127.0.0.1"
PORT = 8765

ALLOWED_ORIGINS = (
    "http://localhost",
    "http://127.0.0.1",
)

def allowed_origin(origin):
    if not origin:
        return False

    return (
        origin.startswith("https://")
        and origin.endswith(".netlify.app")
    ) or any(
        origin == item or origin.startswith(item + ":")
        for item in ALLOWED_ORIGINS
    )

def run_command(command):
    command = command.lower().strip()

    if command in ("status", "hello

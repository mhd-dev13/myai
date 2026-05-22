from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib.parse import urlparse, parse_qs
import subprocess
import re
import os

# =========================
# FILES
# =========================

HTML = open("templates/index.html").read()

ADMIN_HTML = open("templates/admin.html").read()

CHAT_FILE = "data/chat.json"

SETTINGS_FILE = "data/settings.json"

MODEL_PATH = "/data/data/com.termux/files/home/llama.cpp/models/Phi-3-mini-4k-instruct-q4.gguf"

LLAMA_CLI = "/data/data/com.termux/files/home/llama.cpp/build/bin/llama-cli"

# =========================
# DEFAULT SETTINGS
# =========================

DEFAULT_SETTINGS = {

    "system_prompt":
    "تو یک دستیار فارسی طبیعی، دوستانه و کوتاه‌گو هستی.",

    "temperature":
    "0.5"
}

# =========================
# SETTINGS
# =========================

def load_settings():

    if not os.path.exists(SETTINGS_FILE):

        save_settings(DEFAULT_SETTINGS)

    with open(SETTINGS_FILE, "r") as f:

        return json.load(f)

def save_settings(data):

    with open(SETTINGS_FILE, "w") as f:

        json.dump(data, f)

# =========================
# CHAT MEMORY
# =========================

def load_chat():

    if not os.path.exists(CHAT_FILE):

        with open(CHAT_FILE, "w") as f:

            json.dump([], f)

    with open(CHAT_FILE, "r") as f:

        return json.load(f)

def save_chat(messages):

    with open(CHAT_FILE, "w") as f:

        json.dump(messages, f)

# =========================
# CLEAN RESPONSE
# =========================

def clean_response(text):

    text = re.sub(r"\s+", " ", text)

    text = text.strip()

    return text

# =========================
# BUILD CONTEXT
# =========================

def build_context(messages, prompt, settings):

    context = f"""
دستور:
{settings["system_prompt"]}

"""

    recent_messages = messages[-2:]

    for msg in recent_messages:

        context += f"""
کاربر:
{msg['user']}

دستیار:
{msg['ai']}

"""

    context += f"""
کاربر:
{prompt}

دستیار:
"""

    return context

# =========================
# GENERATE RESPONSE
# =========================

def generate_ai_response(prompt, messages):

    settings = load_settings()

    full_prompt = build_context(
        messages,
        prompt,
        settings
    )

    result = subprocess.run(
        [
            LLAMA_CLI,

            "-m",
            MODEL_PATH,

            "--temp",
            settings["temperature"],

            "--top-k",
            "40",

            "--top-p",
            "0.9",

            "--repeat-penalty",
            "1.1",

            "--ctx-size",
            "2048",

            "-n",
            "80",

            "--no-display-prompt",

            "-p",
            full_prompt
        ],
        capture_output=True,
        text=True
    )

    output = result.stdout.strip()

    ai_response = clean_response(output)

    if ai_response == "":

        ai_response = "متوجه نشدم."

    return ai_response

# =========================
# HTTP SERVER
# =========================

class AIHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        parsed = urlparse(self.path)

        # =====================
        # HOME
        # =====================

        if parsed.path == "/":

            self.send_response(200)

            self.send_header(
                "Content-type",
                "text/html"
            )

            self.end_headers()

            self.wfile.write(
                HTML.encode()
            )

        # =====================
        # ADMIN
        # =====================

        elif parsed.path == "/admin":

            self.send_response(200)

            self.send_header(
                "Content-type",
                "text/html"
            )

            self.end_headers()

            self.wfile.write(
                ADMIN_HTML.encode()
            )

        # =====================
        # CHAT
        # =====================

        elif parsed.path == "/chat":

            query = parse_qs(parsed.query)

            prompt = query.get(
                "prompt",
                [""]
            )[0]

            messages = load_chat()

            try:

                ai_response = generate_ai_response(
                    prompt,
                    messages
                )

            except Exception as e:

                ai_response = str(e)

            messages.append({

                "user": prompt,

                "ai": ai_response
            })

            save_chat(messages)

            response = {

                "response": ai_response
            }

            self.send_response(200)

            self.send_header(
                "Content-type",
                "application/json"
            )

            self.end_headers()

            self.wfile.write(
                json.dumps(response).encode()
            )

        # =====================
        # HISTORY
        # =====================

        elif parsed.path == "/history":

            messages = load_chat()

            self.send_response(200)

            self.send_header(
                "Content-type",
                "application/json"
            )

            self.end_headers()

            self.wfile.write(
                json.dumps(messages).encode()
            )

        # =====================
        # CLEAR MEMORY
        # =====================

        elif parsed.path == "/clear_memory":

            save_chat([])

            self.send_response(200)

            self.end_headers()

            self.wfile.write(
                b"Memory Cleared"
            )

        # =====================
        # SAVE PROMPT
        # =====================

        elif parsed.path == "/save_prompt":

            query = parse_qs(parsed.query)

            text = query.get(
                "text",
                [""]
            )[0]

            settings = load_settings()

            settings["system_prompt"] = text

            save_settings(settings)

            self.send_response(200)

            self.end_headers()

            self.wfile.write(
                b"Saved"
            )

        # =====================
        # SAVE SETTINGS
        # =====================

        elif parsed.path == "/save_settings":

            query = parse_qs(parsed.query)

            temp = query.get(
                "temp",
                ["0.5"]
            )[0]

            settings = load_settings()

            settings["temperature"] = temp

            save_settings(settings)

            self.send_response(200)

            self.end_headers()

            self.wfile.write(
                b"Saved"
            )

# =========================
# START SERVER
# =========================

server = HTTPServer(
    ("0.0.0.0", 8000),
    AIHandler
)

print("AI System Running")

server.serve_forever()

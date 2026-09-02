import json
import os
import random
from flask import Flask, render_template, request

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ABOUT_FILES_PATH = os.path.join(BASE_DIR, "data", "about_files.json")
QUOTES_PATH = os.path.join(BASE_DIR, "data", "quotes.json")

def load_about_files():
    with open(ABOUT_FILES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def load_quotes():
    with open(QUOTES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def list_files_text(files):
    return "  ".join(sorted(files.keys()))

# basic terminal window
def run_command(cmd, files):
    """
    Very small fake-shell command handler.
    Supports: ls, pwd, cat <filename>. Anything else -> sorry, this is a fake terminal.
    Returns a dict: {"text": str, "error": bool}
    """
    parts = cmd.split()
 
    if not parts:
        return None
 
    command = parts[0]

    if command == "clear" and len(parts) == 1:
        return {"text": list_files_text(files), "error": False}
 
    if command == "pwd" and len(parts) == 1:
        return {"text": "/home/adi/portfolio/about", "error": False}
 
    if command == "cat" and len(parts) == 2:
        filename = parts[1]
        if filename in files:
            return {"text": files[filename], "error": False}
        return {"text": f"cat: {filename}: No such file or directory", "error": True}
 
    return {"text": f"zsh: command not found: {cmd} \n(sorry this isn't a real terminal)", "error": True}

@app.route("/")
def index():
    quote = random.choice(load_quotes())
    return render_template("index.html", quote=quote)

@app.route("/about")
def about():
    files = load_about_files()
    filenames = sorted(files.keys())

    cmd = request.args.get("cmd", "").strip() or "cat how_to_use.txt"
    result = run_command(cmd, files)

    return render_template("about.html", filenames=filenames, cmd=cmd, result=result)

@app.route("/cs-projects")
def csprojects():
    return render_template("csprojects.html")

@app.route("/reading-writing")
def readingwriting():
    return render_template("readingwriting.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug=True, port=5001)

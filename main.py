import json
import os
import random
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash

# forms + contact page + emails
import smtplib
import fcntl
from datetime import datetime, timezone
from email.message import EmailMessage
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Email, Length
# --------------------

load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me") # contact

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ABOUT_FILES_PATH = os.path.join(BASE_DIR, "data", "about_files.json")
QUOTES_PATH = os.path.join(BASE_DIR, "data", "quotes.json")
CONTACT_PATH = os.path.join(BASE_DIR, "data", "contacts.json") # contact

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

# contact stuff
# ............

class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=128)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=128)])
    subject = StringField("Subject", validators=[DataRequired(), Length(max=128)])
    message = TextAreaField("Message", validators=[DataRequired(), Length(max=2000)])
    company = HiddenField()

def save_contact(name, email, subject, message):
    os.makedirs(os.path.dirname(CONTACT_PATH), exist_ok=True)
    if not os.path.exists(CONTACT_PATH):
        with open(CONTACT_PATH, "w", encoding="utf-8") as f:
            f.write("{}")

    with open(CONTACT_PATH, "r+", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.seek(0)
        content = f.read()
        contacts = json.loads(content) if content else {}

        key = email.strip().lower()
        is_new = key not in contacts
        entry = {
            "subject": subject,
            "message": message,
            "sent_at": datetime.now(timezone.utc).isoformat(),
        }

        if is_new:
            contacts[key] = {
                "name": name,
                "email": email,
                "first_contacted": entry["sent_at"],
                "messages": [entry],
            }
        else:
            contacts[key]["messages"].append(entry)

        f.seek(0)
        f.truncate()
        json.dump(contacts, f, indent=2)
        fcntl.flock(f, fcntl.LOCK_UN)

    return is_new


SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 465))
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
CONTACT_INBOX = os.environ.get("CONTACT_INBOX", SMTP_USER)

def send_contact_email(name, email, subject, message):
    if not SMTP_USER or not SMTP_PASSWORD:
        print("SMTP not configured - skipping email send.")
        return

    msg = EmailMessage()
    msg["Subject"] = f"[Portfolio Contact] {subject}"
    msg["From"] = SMTP_USER
    msg["To"] = CONTACT_INBOX
    msg["Reply-To"] = email
    msg.set_content(f"From: {name} <{email}>\n\n{message}")

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)

# ............


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

# Updated form thing stuff :)
@app.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()

    if form.validate_on_submit():
        if form.company.data:
            return redirect(url_for("contact"))

        save_contact(form.name.data, form.email.data, form.subject.data, form.message.data)
        send_contact_email(form.name.data, form.email.data, form.subject.data, form.message.data)

        flash("Message sent - thanks for reaching out, I'll get back to you as soon as I get the chance.", "success")
        return redirect(url_for("contact"))
    
    return render_template("contact.html", form=form)

if __name__ == "__main__":
    app.run(debug=True, port=5001)

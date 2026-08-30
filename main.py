from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

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

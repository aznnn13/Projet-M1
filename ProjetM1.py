from flask import Flask
from flask import render_template

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
# Powershell = $env:FLASK_APP = "ProjetM1"
# cmd = set FLASK_APP=ProjetM1
# flask run

@app.route('/')
def index():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True)
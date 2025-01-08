from flask import Flask

app = Flask(__name__)


@app.route("/available_hosts", methods=["GET"])
def available_hosts():
    return []


@app.route("/connect", methods=["POST"])
def connect():
    return []


app.run(host="127.0.0.1", port=3000, debug=True)

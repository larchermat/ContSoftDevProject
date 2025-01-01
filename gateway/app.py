from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

@app.route("/<path:service>/<path:subpath>")
def services(service, subpath):
    args = ""
    if request.args:
        args = "?" + "&".join([f"{pair[0]}={pair[1]}" for pair in request.args.items()])
    url = f"http://{service}:5000/{subpath}{args}"
    res = requests.get(url)
    cont_type = res.headers.get("Content-Type").split(";")[0] 
    if cont_type == "text/html":
        ret = res.text
    elif cont_type == "application/json":
        ret = res.json()
    else:
        ret = ""
    return ret, res.status_code

@app.route("/")
def index():
    message = {"message": "Welcome"}
    return jsonify(message), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
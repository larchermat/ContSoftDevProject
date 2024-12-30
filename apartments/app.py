from flask import Flask, jsonify, request
import threading
import db_interaction as dbi
import rabbitMQ_interaction as rmq

app = Flask(__name__)

def check_args(args:list, request):
    ret = []
    for arg in args:
        val = request.args.get(arg)
        if not val:
            raise Exception(jsonify({"error": f"Arg {arg} is required!"}))
        ret.append(val)
    return ret

@app.route("/add")
def create():
    try:
        name, address, noiselevel, floor = check_args(["name", "address", "noiselevel", "floor"], request)
    except Exception as e:
        return e.args[0], 400
    id = dbi.add_apartment(
        name=name, address=address, noiselevel=noiselevel, floor=floor
    )
    new_apart_thread = threading.Thread(
        target=rmq.publish_event,
        args=(
            "events",
            "apartment.new",
            dbi.Apartment(id, name, address, noiselevel, floor).__dict__,
        ),
    )
    new_apart_thread.daemon = True
    new_apart_thread.start()
    return "", 200

@app.route("/remove")
def remove():
    try:
        id, = check_args(["id"],request)
    except Exception as e:
        return e.args[0], 400
    dbi.remove_apartment(id)
    new_apart_thread = threading.Thread(
        target=rmq.publish_event, args=("events", "apartment.remove", {"id": id})
    )
    new_apart_thread.daemon = True
    new_apart_thread.start()
    return "", 200


@app.route("/list")
def list_items():
    entries = dbi.get_all_apartments()
    return jsonify([entry.__dict__ for entry in entries]), 200


@app.route("/")
def index():
    message = {"message": "Welcome"}
    return jsonify(message), 200


if __name__ == "__main__":
    dbi.initialize()
    app.run(host="0.0.0.0", port=5000)

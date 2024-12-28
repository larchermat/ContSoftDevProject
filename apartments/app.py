from flask import Flask, jsonify, request
import threading
import db_interaction as dbi
import rabbitMQ_interaction as rmq
import os

app = Flask(__name__)

@app.route('/add')
def create():
    name = request.args.get('name')
    address = request.args.get('address')
    noiselevel = request.args.get('noiselevel')
    floor = request.args.get('floor')
    if not name:
        return jsonify({"error": "Name is required!"}), 400
    elif not address:
        return jsonify({"error": "Address is required!"}), 400
    elif not noiselevel:
        return jsonify({"error": "Noise level is required!"}), 400
    elif not floor:
        return jsonify({"error": "Floor is required!"}), 400
    else:
        id = dbi.add_apartment(name=name, address=address, noiselevel=noiselevel, floor=floor)
        new_apart_thread = threading.Thread(target=rmq.publish_new_apartments, args=(id,))
        new_apart_thread.daemon = True
        new_apart_thread.start()
        return '', 200

@app.route('/remove')
def remove():
    id = request.args.get('id')
    if not id:
        return jsonify({"error": "Missing 'id' parameter"}), 400
    print(f"id:{id}")
    dbi.remove_apartment(id)
    new_apart_thread = threading.Thread(target=rmq.publish_rem_apartments, args=(id,))
    new_apart_thread.daemon = True
    new_apart_thread.start()
    return '', 200

@app.route('/list')
def list_items():
    entries = dbi.get_all_apartments()
    return jsonify([entry.__dict__ for entry in entries]), 200

@app.route('/')
def index():
    message = {"message":"Welcome"}
    return jsonify(message), 200

if __name__ == '__main__':
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        dbi.initialize()
    app.run(host='0.0.0.0', port=5000, debug=True)
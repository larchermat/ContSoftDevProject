from flask import Flask, jsonify, request
import threading
import db_interaction as dbi
import rabbitMQ_interaction as rmq

app = Flask(__name__)

@app.route('/add')
def create():
    apartment = request.args.get('apartment')
    start = request.args.get('from')
    end = request.args.get('to')
    who = request.args.get('who')
    if not apartment:
        return jsonify({"error": "Apartment id is required!"}), 400
    elif not start:
        return jsonify({"error": "Start date is required!"}), 400
    elif not end:
        return jsonify({"error": "End date level is required!"}), 400
    elif not who:
        return jsonify({"error": "Who is required!"}), 400
    else:
        dbi.add_booking(apartment=apartment, start=start, end=end, who=who)
        return '', 200

@app.route('/cancel')
def cancel():
    id = request.args.get('id')
    if not id:
        return jsonify({"error": "Missing 'id' parameter"}), 400
    dbi.cancel_booking(id)
    return '', 200

@app.route('/list')
def list_bookings():
    entries = dbi.get_all_bookings()
    return jsonify([entry.__dict__ for entry in entries]), 200

@app.route('/list_apartments')
def list_apartments():
    entries = dbi.get_all_apartments()
    return jsonify([{"id":entry} for entry in entries]), 200

@app.route('/')
def index():
    message = {"message":"Welcome"}
    return jsonify(message), 200

if __name__ == '__main__':
    dbi.initialize()
    consumer_thread = threading.Thread(target=rmq.start_consumer)
    consumer_thread.daemon = True
    consumer_thread.start()
    app.run(host='0.0.0.0', port=5000, debug=True)
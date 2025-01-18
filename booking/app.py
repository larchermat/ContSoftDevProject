from flask import Flask, jsonify, request
import threading
import db_interaction as dbi
import rabbitMQ_interaction as rmq
import datetime
import time
import requests

app = Flask(__name__)

def wait_for_apartments():
    max_retries = 10
    retry_interval = 5
    for attempt in range(max_retries):
        try:
            res = requests.get("http://apartments:5000/list")
            return res.json()
        except requests.exceptions.ConnectionError as e:
            print(
                f"Apartments not ready, retrying in {retry_interval} seconds... (Attempt {attempt + 1}/{max_retries})"
            )
            time.sleep(retry_interval)
    print("Apartments service is still unavailable after max retries. Exiting.")
    raise Exception("Could not retrieve data from Apartments after multiple retries.")

def check_args(args:list, request):
    ret = []
    for arg in args:
        val = request.args.get(arg)
        if not val:
            raise Exception(jsonify({"error": f"Arg {arg} is required!"}))
        ret.append(val)
    return ret

def check_dates(start: str, end: str):
    try:
        start_date = datetime.datetime.strptime(start, "%Y%m%d")
    except Exception as e:
        raise Exception(str(e), jsonify({"error": "Start date is incorrectly set", "start": start}))
    try:
        end_date = datetime.datetime.strptime(end, "%Y%m%d")
    except Exception as e:
        raise Exception(str(e), jsonify({"error": "End date is incorrectly set", "end": end}))
    if end_date <= start_date:
            raise Exception(
                "End date is equal to or before start date",
                jsonify(
                    {
                        "error": "End date is equal to or before start date",
                        "start": start_date.strftime("%d/%m/%Y"),
                        "end": end_date.strftime("%d/%m/%Y"),
                    }
                )
            )


@app.route("/add")
def add():
    try:
        apartment, start, end, who = check_args(["apartment", "from", "to", "who"], request)
    except Exception as e:
        return e.args[0], 400
    try:
        check_dates(start, end)
    except Exception as e:
        return (
            e.args[1],
            406,
        )
    try:
        id = dbi.add_booking(apartment=apartment, start=start, end=end, who=who)
    except dbi.BookingUnavailableException as e:
        return jsonify({"error":f"{str(e)}"}), 400
    new_booking_thread = threading.Thread(
        target=rmq.publish_event,
        args=(
            "events",
            "booking.new",
            dbi.Booking(id, apartment, start, end, who).dict_for_mq(),
        ),
    )
    new_booking_thread.daemon = True
    new_booking_thread.start()
    return "", 200


@app.route("/cancel")
def cancel():
    try:
        id, = check_args(["id"],request)
    except Exception as e:
        return e.args[0], 400
    dbi.cancel_booking(id)
    cancel_booking_thread = threading.Thread(
        target=rmq.publish_event, args=("events", "booking.remove", {"id": id})
    )
    cancel_booking_thread.daemon = True
    cancel_booking_thread.start()
    return "", 200

@app.route("/change")
def change():
    try:
        id, start, end = check_args(["id", "from", "to"], request)
    except Exception as e:
        return e.args[0], 400
    try:
        check_dates(start, end)
    except Exception as e:
        return (
            e.args[1],
            406,
        )
    try:
        booking = dbi.change_booking(id, start, end)
    except dbi.BookingUnavailableException as e:
        return jsonify({"error":f"{str(e)}"}), 400
    change_booking_thread = threading.Thread(
        target=rmq.publish_event,
        args=(
            "events",
            "booking.change",
            booking.dict_for_mq(),
        ),
    )
    change_booking_thread.daemon = True
    change_booking_thread.start()
    return '', 200
    
@app.route("/list")
def list_bookings():
    entries = dbi.get_all_bookings()
    return jsonify([entry.__dict__ for entry in entries]), 200

@app.route("/list_apartments")
def list_apartments():
    entries = dbi.get_all_apartments()
    return jsonify([{"id": entry} for entry in entries]), 200

@app.route("/")
def index():
    message = {"message": "Welcome"}
    return jsonify(message), 200

if __name__ == "__main__":
    apartments = wait_for_apartments()
    dbi.initialize(apartments)
    channel = rmq.set_up_consumer()
    consumer_thread = threading.Thread(target=rmq.start_consumer, args=(channel,))
    consumer_thread.daemon = True
    consumer_thread.start()
    app.run(host="0.0.0.0", port=5000)
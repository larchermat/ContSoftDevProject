from flask import Flask, jsonify, request
import threading
import db_interaction as dbi
import rabbitMQ_interaction as rmq
import datetime

app = Flask(__name__)

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
    return start_date, end_date

@app.route("/list_apartments")
def list_apartments():
    entries = dbi.get_all_apartments()
    return jsonify([entry.__dict__ for entry in entries])

@app.route("/list_bookings")
def list_bookings():
    entries = dbi.get_all_bookings()
    return jsonify([entry.__dict__ for entry in entries])

@app.route("/search")
def search():
    try:
        start, end = check_args(["from", "to"], request)
    except Exception as e:
        return e.args[0], 400
    try:
        start_date, end_date = check_dates(start, end)
    except Exception as e:
        return (
            e.args[1],
            406
        )
    entries = dbi.get_all_available(start=start_date, end=end_date)
    return jsonify([entry.__dict__ for entry in entries]), 200


@app.route("/")
def index():
    message = {"message": "Welcome"}
    return jsonify(message), 200


if __name__ == "__main__":
    dbi.initialize()
    consumer_thread = threading.Thread(target=rmq.start_consumer)
    consumer_thread.daemon = True
    consumer_thread.start()
    app.run(host="0.0.0.0", port=5000)

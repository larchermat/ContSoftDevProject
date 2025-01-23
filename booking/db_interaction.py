import sqlite3
import uuid
import datetime
import threading

db_lock = threading.Lock()


class BookingUnavailableException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class Booking:
    def __init__(self, id, apartment, start, end, who):
        self.id = id
        self.apartment = apartment
        self.start = datetime.datetime.strptime(start, "%Y%m%d")
        self.end = datetime.datetime.strptime(end, "%Y%m%d")
        self.who = who

    def dict_for_mq(self):
        return {
            "id": self.id,
            "apartment": self.apartment,
            "start": self.start.strftime("%Y%m%d"),
            "end": self.end.strftime("%Y%m%d"),
            "who": self.who,
        }

    def set_start(self, start):
        self.start = datetime.datetime.strptime(start, "%Y%m%d")

    def set_end(self, end):
        self.end = datetime.datetime.strptime(end, "%Y%m%d")


def convert_entry(entry):
    return Booking(
        entry["id"], entry["apartment"], entry["from"], entry["to"], entry["who"]
    )


def get_db_connection():
    conn = sqlite3.connect("booking_db/data.db")
    conn.row_factory = sqlite3.Row
    return conn


def initialize(apartments):
    connection = get_db_connection()
    with connection:
        connection.execute(
            """CREATE TABLE IF NOT EXISTS apartments (
                id VARCHAR(32) PRIMARY KEY
            );"""
        )
        connection.execute(
            """CREATE TABLE IF NOT EXISTS bookings (
                id VARCHAR(32) PRIMARY KEY,
                apartment VARCHAR(32) NOT NULL,
                'from' TEXT NOT NULL,
                'to' TEXT NOT NULL,
                who TEXT NOT NULL,
                FOREIGN KEY (apartment) REFERENCES apartments(id)
            );"""
        )
        if len(apartments) > 0:
            for item in apartments:
                connection.execute(
                    "INSERT OR REPLACE INTO apartments (id) VALUES (?)", (item["id"],)
                )
    connection.commit()
    connection.close()


def get_all_bookings():
    with db_lock:
        connection = get_db_connection()
        entries = connection.execute("SELECT * FROM bookings").fetchall()
        connection.close()
    return [convert_entry(entry) for entry in entries]


def add_apartment(id: str):
    with db_lock:
        connection = get_db_connection()
        connection.execute("INSERT INTO apartments (id) VALUES (?)", (id,))
        connection.commit()
        connection.close()


def remove_apartment(id: str):
    with db_lock:
        connection = get_db_connection()
        with connection:
            connection.execute("DELETE FROM bookings WHERE apartment=?;", (id,))
            connection.execute("DELETE FROM apartments WHERE id=?;", (id,))
        connection.close()


def get_bookings_per_apartment(id: str):
    with db_lock:
        connection = get_db_connection()
        bookings = connection.execute(
            "SELECT * FROM bookings WHERE apartment=?", (id,)
        ).fetchall()
        connection.close()
    return bookings


def check_booking(
    start_str: str, end_str: str, who: str = None, apartment: str = None, id: str = None
):
    start = datetime.datetime.strptime(start_str, "%Y%m%d")
    end = datetime.datetime.strptime(end_str, "%Y%m%d")
    booking = None
    if apartment == None or who == None:
        with db_lock:
            connection = get_db_connection()
            booking = convert_entry(
                connection.execute(
                    "SELECT * FROM bookings WHERE id=?", (id,)
                ).fetchone()
            )
            connection.close()
            apartment = booking.apartment
            who = booking.who
    bookings = get_bookings_per_apartment(apartment)
    bookings = [convert_entry(entry) for entry in bookings]
    isValid = True
    for b in bookings:
        if (
            (b.end > start and b.start <= end) or (b.start < end and b.end >= start)
        ) and (who != b.who):
            booking = b
            isValid = False
            break
    if not isValid:
        raise BookingUnavailableException(
            "Booking dates are not available",
            {
                "start": f"{start}",
                "end": f"{end}",
                "who": f"{who}",
                "apartment": f"{apartment}",
            },
            booking.__dict__,
        )


def add_booking(apartment: str, start: str, end: str, who: str):
    check_booking(start_str=start, end_str=end, who=who, apartment=apartment)
    with db_lock:
        connection = get_db_connection()
        id = uuid.uuid4().hex
        connection.execute(
            "INSERT INTO bookings (id, apartment, 'from', 'to', who) VALUES (?, ?, ?, ?, ?)",
            (id, apartment, start, end, who),
        )
        connection.commit()
        connection.close()
    return id


def change_booking(id: str, start: str, end: str):
    check_booking(start_str=start, end_str=end, id=id)
    with db_lock:
        connection = get_db_connection()
        booking = convert_entry(
            connection.execute("SELECT * FROM bookings WHERE id=?", (id,)).fetchone()
        )
        connection.execute(
            """
            UPDATE bookings
            SET 'from'=?, 'to'=?
            WHERE id=?
        """,
            (start, end, id),
        )
        connection.commit()
        connection.close()
    booking.set_start(start)
    booking.set_end(end)
    return booking


def cancel_booking(id: str):
    with db_lock:
        connection = get_db_connection()
        connection.execute("DELETE FROM bookings WHERE id=?;", (id,))
        connection.commit()
        connection.close()

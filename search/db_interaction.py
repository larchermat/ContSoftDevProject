import sqlite3
import datetime
import threading

db_lock = threading.Lock()


class Booking:
    def __init__(self, id, apartment, start, end):
        self.id = id
        self.apartment = apartment
        self.start = datetime.datetime.strptime(start, "%Y%m%d")
        self.end = datetime.datetime.strptime(end, "%Y%m%d")


def convert_entry_booking(entry):
    return Booking(entry["id"], entry["apartment"], entry["from"], entry["to"])


class Apartment:
    def __init__(self, id, name, address, noiselevel, floor):
        self.id = id
        self.name = name
        self.address = address
        self.noiselevel = noiselevel
        self.floor = floor


def convert_entry_apartment(entry):
    return Apartment(
        entry["id"],
        entry["name"],
        entry["address"],
        entry["noiselevel"],
        entry["floor"],
    )


def get_db_connection():
    conn = sqlite3.connect("search_db/data.db")
    conn.row_factory = sqlite3.Row
    return conn


def change_date_format(date: str):
    """Example: changes 'Fri, 01 Dec 2023 00:00:00 GMT' to '20231201'"""
    return datetime.datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %Z").strftime(
        "%Y%m%d"
    )


def initialize(apartments, bookings):
    connection = get_db_connection()
    with connection:
        connection.execute(
            """CREATE TABLE IF NOT EXISTS apartments (
                id VARCHAR(32) PRIMARY KEY,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                noiselevel INTEGER NOT NULL,
                floor INTEGER NOT NULL
            );"""
        )
        connection.execute(
            """CREATE TABLE IF NOT EXISTS bookings (
                id VARCHAR(32) PRIMARY KEY,
                apartment VARCHAR(32) NOT NULL,
                'from' TEXT NOT NULL,
                'to' TEXT NOT NULL
            );"""
        )
        if len(apartments) > 0:
            for item in apartments:
                connection.execute(
                    "INSERT OR REPLACE INTO apartments (id, name, address, noiselevel, floor) VALUES (?,?,?,?,?)",
                    (
                        item["id"],
                        item["name"],
                        item["address"],
                        item["noiselevel"],
                        item["floor"],
                    ),
                )
        if len(bookings) > 0:
            for item in bookings:
                connection.execute(
                    "INSERT OR REPLACE INTO bookings (id, apartment, 'from', 'to') VALUES (?, ?, ?, ?)",
                    (
                        item["id"],
                        item["apartment"],
                        change_date_format(item["start"]),
                        change_date_format(item["end"]),
                    ),
                )
    connection.commit()
    connection.close()


def get_all_available(start: datetime.datetime, end: datetime.datetime):
    with db_lock:
        connection = get_db_connection()
        entries = connection.execute("SELECT * FROM bookings").fetchall()
        bookings = [convert_entry_booking(entry) for entry in entries]
        entries = connection.execute("SELECT * FROM apartments").fetchall()
        apartments = [convert_entry_apartment(entry) for entry in entries]
        connection.close()
    available = []
    for apartment in apartments:
        isAvailable = True
        for booking in bookings:
            if apartment.id == booking.apartment and (
                (booking.end > start and booking.start <= end)
                or (booking.start < end and booking.end >= start)
            ):
                isAvailable = False
                break
        if isAvailable:
            available.append(apartment)
    return available


def add_apartment(id: str, name: str, address: str, noiselevel: int, floor: int):
    with db_lock:
        connection = get_db_connection()
        connection.execute(
            "INSERT INTO apartments (id, name, address, noiselevel, floor) VALUES (?, ?, ?, ?, ?)",
            (id, name, address, noiselevel, floor),
        )
        connection.commit()
        connection.close()


def remove_apartment(id: str):
    with db_lock:
        connection = get_db_connection()
        connection.execute("DELETE FROM apartments WHERE id=?;", (id,))
        connection.commit()
        connection.close()


def add_booking(id: str, apartment: str, start: str, end: str):
    with db_lock:
        connection = get_db_connection()
        connection.execute(
            "INSERT INTO bookings (id, apartment, 'from', 'to') VALUES (?, ?, ?, ?)",
            (id, apartment, start, end),
        )
        connection.commit()
        connection.close()


def remove_booking(id: str):
    with db_lock:
        connection = get_db_connection()
        connection.execute("DELETE FROM bookings WHERE id=?;", (id,))
        connection.commit()
        connection.close()


def change_booking(id: str, start: str, end: str):
    with db_lock:
        connection = get_db_connection()
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

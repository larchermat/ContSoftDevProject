import sqlite3
import uuid

class Apartment:
    def __init__(self, id, apartment, start, end, who):
        self.id=id
        self.apartment=apartment
        self.start = start
        self.end = end
        self.who = who

def convert_entry(entry):
    return Apartment(
        entry["id"],
        entry["apartment"],
        entry["from"],
        entry["to"],
        entry["who"]
        )

def get_db_connection():
    conn = sqlite3.connect('booking_db/data.db')
    conn.row_factory = sqlite3.Row
    return conn

def initialize():
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
    connection.commit()
    connection.close()

def get_all_bookings():
    connection = get_db_connection()
    entries = connection.execute('SELECT * FROM bookings').fetchall()
    return [convert_entry(entry) for entry in entries]

def get_all_apartments():
    connection = get_db_connection()
    entries = connection.execute('SELECT * FROM apartments').fetchall()
    return [entry['id'] for entry in entries]

def add_apartment(id:str):
    connection = get_db_connection()
    connection.execute("INSERT INTO apartments (id) VALUES (?)", (id,))
    connection.commit()
    connection.close()

def remove_apartment(id:str):
    connection = get_db_connection()
    connection.execute("DELETE FROM bookings WHERE apartment=?;",(id,))
    connection.execute("DELETE FROM apartments WHERE id=?;",(id,))
    connection.commit()
    connection.close()

def add_booking(apartment:str, start:str, end:str, who:str):
    connection = get_db_connection()
    id = uuid.uuid4().hex
    connection.execute("INSERT INTO bookings (id, apartment, 'from', 'to', who) VALUES (?, ?, ?, ?, ?)", (id, apartment, start, end, who))
    connection.commit()
    connection.close()

def remove_booking(id:str):
    connection = get_db_connection()
    connection.execute("DELETE FROM bookings WHERE id=?;",(id,))
    connection.commit()
    connection.close()
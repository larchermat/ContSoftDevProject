import sqlite3
import uuid


class Apartment:
    def __init__(self, id: str, name: str, address: str, noiselevel: int, floor: int):
        self.id = id
        self.name = name
        self.address = address
        self.noiselevel = noiselevel
        self.floor = floor


def convert_entry(entry):
    return Apartment(
        entry["id"],
        entry["name"],
        entry["address"],
        entry["noiselevel"],
        entry["floor"],
    )


def get_db_connection():
    conn = sqlite3.connect("apartments_db/data.db")
    conn.row_factory = sqlite3.Row
    return conn


def initialize():
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
    connection.commit()
    connection.close()


def get_all_apartments():
    connection = get_db_connection()
    entries = connection.execute("SELECT * FROM apartments").fetchall()
    connection.close()
    return [convert_entry(entry) for entry in entries]


def add_apartment(name: str, address: str, noiselevel: int, floor: int):
    connection = get_db_connection()
    id = uuid.uuid4().hex
    connection.execute(
        "INSERT INTO apartments (id, name, address, noiselevel, floor) VALUES (?, ?, ?, ?, ?)",
        (id, name, address, noiselevel, floor),
    )
    connection.commit()
    connection.close()
    return id


def remove_apartment(id: str):
    connection = get_db_connection()
    connection.execute("DELETE FROM apartments WHERE id=?;", (id,))
    connection.commit()
    connection.close()

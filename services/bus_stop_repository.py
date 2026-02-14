import sqlite3
from typing import List, Dict

DB_NAME = "bus_stops.db"


def get_connection():
    """
    Creates a new SQLite connection.
    FastAPI should NOT reuse connections globally for SQLite.
    """
    return sqlite3.connect(DB_NAME)


def get_all_bus_stops() -> List[Dict]:
    """
    Returns all bus stops from the database.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT bus_stop_code, description, latitude, longitude
        FROM bus_stops
    """)

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "bus_stop_code": row[0],
            "description": row[1],
            "latitude": row[2],
            "longitude": row[3]
        }
        for row in rows
    ]


def get_bus_stop_by_code(bus_stop_code: str) -> Dict | None:
    """
    Returns a single bus stop by code.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT bus_stop_code, description, latitude, longitude
        FROM bus_stops
        WHERE bus_stop_code = ?
    """, (bus_stop_code,))

    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "bus_stop_code": row[0],
            "description": row[1],
            "latitude": row[2],
            "longitude": row[3]
        }

    return None
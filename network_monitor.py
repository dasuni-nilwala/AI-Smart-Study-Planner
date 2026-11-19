
import sqlite3
from datetime import datetime


# Database connection
def connect_db():
    return sqlite3.connect("study_planner.db")


# Create network activity table
def create_network_table():

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS network_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT NOT NULL,
            protocol TEXT NOT NULL,
            message TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


# Save network activity permanently
def log_activity(protocol, message, status="Success"):

    connection = connect_db()
    cursor = connection.cursor()

    current_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute("""
        INSERT INTO network_logs
        (time, protocol, message, status)
        VALUES (?, ?, ?, ?)
    """, (current_time, protocol, message, status))

    connection.commit()
    connection.close()


# Retrieve saved network activities
def get_network_logs():

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT time, protocol, message, status
        FROM network_logs
        ORDER BY id DESC
    """)

    logs = cursor.fetchall()

    connection.close()

    return [
        {
            "time": log[0],
            "protocol": log[1],
            "message": log[2],
            "status": log[3]
        }
        for log in logs
    ]


# Clear network activity history
def clear_network_logs():

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM network_logs")

    connection.commit()
    connection.close()


# Create the table when this module is initialized
create_network_table()


import sqlite3

DATABASE_NAME = "study_planner.db"


def connect_db():
    return sqlite3.connect(DATABASE_NAME)


def create_table():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            subject TEXT NOT NULL,
            deadline TEXT NOT NULL,
            priority TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'Pending'
        )
    """)

    connection.commit()
    connection.close()


def add_task(task, subject, deadline, priority, description):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO tasks
        (task, subject, deadline, priority, description)
        VALUES (?, ?, ?, ?, ?)
    """, (task, subject, deadline, priority, description))

    connection.commit()
    connection.close()


def get_tasks():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM tasks")

    tasks = cursor.fetchall()

    connection.close()

    return tasks

def update_task_status(task_id, status):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE tasks
        SET status = ?
        WHERE id = ?
    """, (status, task_id))

    connection.commit()
    connection.close()

def save_study_plan(plan):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_name TEXT NOT NULL,
            priority TEXT NOT NULL,
            days_left INTEGER NOT NULL,
            score INTEGER NOT NULL,
            position INTEGER NOT NULL
        )
    """)

    cursor.execute("DELETE FROM study_plans")

    for position, task in enumerate(plan, start=1):
        cursor.execute("""
            INSERT INTO study_plans
            (task_name, priority, days_left, score, position)
            VALUES (?, ?, ?, ?, ?)
        """, (
            task["task"],
            task["priority"],
            task["days_left"],
            task["score"],
            position
        ))

    connection.commit()
    connection.close()

def get_saved_study_plan():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM study_plans
        ORDER BY position ASC
    """)

    plan = cursor.fetchall()

    connection.close()

    return plan

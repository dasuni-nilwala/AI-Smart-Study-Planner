
import socket
import json
import database

HOST = "127.0.0.1"
PORT = 5000

database.create_table()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind((HOST, PORT))
server.listen()

print("AI Study Planner TCP Server is running...")
print(f"Listening on {HOST}:{PORT}")

while True:
    connection, address = server.accept()

    print("Connected by:", address)

    try:
        data = connection.recv(4096).decode()
        request = json.loads(data)

        action = request.get("action")

        if action == "add_task":
            database.add_task(
                request["task"],
                request["subject"],
                request["deadline"],
                request["priority"],
                request["description"]
            )

            response = {
                "success": True,
                "message": "Task added successfully!"
            }

        elif action == "get_tasks":
            tasks = database.get_tasks()

            response = {
                "success": True,
                "tasks": tasks
            }

        elif action == "update_status":
            database.update_task_status(
                request["task_id"],
                request["status"]
            )

            response = {
                "success": True,
                "message": "Task status updated!"
            }

        else:
            response = {
                "success": False,
                "message": "Unknown action"
            }

    except Exception as error:
        response = {
            "success": False,
            "message": str(error)
        }

    connection.sendall(json.dumps(response).encode())
    connection.close()

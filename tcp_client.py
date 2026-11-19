
import socket
import json

HOST = "127.0.0.1"
PORT = 5000


def send_request(request):

    client = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    client.connect((HOST, PORT))

    message = json.dumps(request)

    client.sendall(message.encode())

    response = client.recv(4096).decode()

    client.close()

    return json.loads(response)


# Test TCP communication
if __name__ == "__main__":

    request = {
        "action": "get_tasks"
    }

    response = send_request(request)

    print("TCP Server Response:")
    print(response)

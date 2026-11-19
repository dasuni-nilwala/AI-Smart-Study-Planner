
import socket

HOST = "127.0.0.1"
PORT = 6000


def send_status(message):

    client = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    client.settimeout(3)

    try:
        client.sendto(message.encode(), (HOST, PORT))

        response, address = client.recvfrom(1024)

        return response.decode()

    except socket.timeout:
        return "UDP server did not respond."

    except OSError as error:
        return f"UDP error: {error}"

    finally:
        client.close()

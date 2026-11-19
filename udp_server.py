
import socket

HOST = "127.0.0.1"
PORT = 6000

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server.bind((HOST, PORT))

print("UDP Server is running...")
print(f"Listening on {HOST}:{PORT}")

while True:

    data, address = server.recvfrom(1024)

    message = data.decode()

    print("Received message:", message)

    response = "UDP status received successfully!"

    server.sendto(response.encode(), address)

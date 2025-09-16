# test_login_client.py
import socket
import json

HOST = "127.0.0.1"
PORT = 5000  # same as your server

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        print("Connected to server")

        # Login message
        login_msg = {
            "action": "login",
            "data": {
                "username": "testuser2",
                "password": "password123"
            }
        }

        # Send JSON string with newline
        sock.sendall((json.dumps(login_msg) + "\n").encode("utf-8"))

        # Receive response
        response = sock.recv(4096).decode("utf-8")
        print("Received:", response)

if __name__ == "__main__":
    main()

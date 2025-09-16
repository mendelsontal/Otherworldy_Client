import socket
import json

sock = socket.socket()
sock.connect(("127.0.0.1", 5000))
print("Connected to server")

# Must be a dict with action + data
login_message = {
    "action": "login",
    "data": {"username": "testuser", "password": "1234"}
}

# Convert to JSON, add newline so server can split
sock.sendall((json.dumps(login_message) + "\n").encode("utf-8"))

# Receive response
response = sock.recv(4096)
print("Received:", response.decode())
sock.close()

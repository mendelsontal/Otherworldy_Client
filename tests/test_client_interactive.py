# test_client_interactive.py
import socket
import json

HOST = "127.0.0.1"
PORT = 5000

def send_message(sock, message_dict):
    message_str = json.dumps(message_dict) + "\n"
    sock.sendall(message_str.encode("utf-8"))

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        print(f"Connected to server at {HOST}:{PORT}")

        # Login
        username = input("Username: ")
        password = input("Password: ")
        send_message(sock, {"action": "login", "data": {"username": username, "password": password}})

        while True:
            try:
                # Receive messages
                data = sock.recv(4096)
                if not data:
                    print("Server disconnected")
                    break
                for line in data.decode("utf-8").split("\n"):
                    if line.strip():
                        print("Received:", line)

                # Send commands
                cmd = input("Command (JSON) or 'quit' to exit: ")
                if cmd.lower() == "quit":
                    break
                try:
                    message = json.loads(cmd)
                    send_message(sock, message)
                except json.JSONDecodeError:
                    print("Invalid JSON")
            except KeyboardInterrupt:
                print("\nExiting...")
                break

if __name__ == "__main__":
    main()

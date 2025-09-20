# client/network/client.py
import socket
import threading
import json

class GameClient:
    def __init__(self, host="127.0.0.1", port=5000):
        self.host = host
        self.port = port
        self.sock = None
        self.recv_thread = None
        self.running = False
        self.on_message = None  # callback for received messages

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.running = True
        self.recv_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self.recv_thread.start()
        print(f"[+] Connected to server {self.host}:{self.port}")

    @property
    def connected(self):
        return self.sock is not None and self.running

    def _receive_loop(self):
        buffer = ""
        while self.running:
            try:
                data = self.sock.recv(4096)
                if not data:
                    print("[!] Server disconnected")
                    self.running = False
                    break
                buffer += data.decode("utf-8")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line.strip():
                        try:
                            message = json.loads(line)
                            if self.on_message:
                                self.on_message(message)
                        except Exception as e:
                            print(f"[!] Failed to parse server message: {line} - {e}")
            except Exception as e:
                print(f"[!] Receive error: {e}")
                self.running = False
                break

    def send_json(self, data: dict):
        """Helper to send JSON messages to the server."""
        try:
            self.send(json.dumps(data))   # always dumps here
        except Exception as e:
            print(f"[!] Failed to send JSON: {e}")

    def send(self, message: str):
        """Send a raw string message to the server (expects string)."""
        if not self.sock:
            raise RuntimeError("Client not connected")
        try:
            self.sock.sendall((message + "\n").encode("utf-8"))
        except Exception as e:
            print(f"[!] Failed to send message: {e}")

    def login(self, username: str, password: str):
        self.send_json({
            "action": "login",
            "data": {"username": username, "password": password}
        })
    
    def close(self):
        self.running = False
        if self.sock:
            self.sock.close()
            self.sock = None

    def delete_character(self, char_id):
        if not self.connected:
            self.connect()  # try to reconnect
        self.send_json({
            "action": "delete_character",
            "char_id": char_id
        })


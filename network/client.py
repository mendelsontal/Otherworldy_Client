# client/network/client.py
import socket
import threading
import json
import queue
import time
from client.data import config

class GameClient:
    def __init__(self, host=config.SERVER_IP, port=5000):
        self.host = host
        self.port = port
        self.sock = None
        self.recv_thread = None
        self.running = False
        self.on_message = None
        self._response_queue = queue.Queue()  # queue for all messages

        self.logged_in = False
        self.user_id = None
        self._last_login = None
        self._login_lock = threading.Lock()  # prevent simultaneous relogin attempts

    # ---------------- Connection ----------------
    def connect(self):
        if self.connected:
            return
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.running = True
        self.recv_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self.recv_thread.start()
        print(f"[+] Connected to server {self.host}:{self.port}")

        # Trigger relogin asynchronously if needed
        if self._last_login:
            threading.Thread(target=self._relogin_if_needed, daemon=True).start()

    @property
    def connected(self):
        return self.sock is not None and self.running

    # ---------------- Auto Relogin ----------------
    def _relogin_if_needed(self):
        with self._login_lock:
            if self._last_login and not self.logged_in:
                username, password = self._last_login
                print("[*] Re-sending login after reconnect...")
                self.send_json({
                    "action": "login",
                    "data": {"username": username, "password": password}
                })
                # Do NOT block here: `_receive_loop` will handle response and set logged_in

    # ---------------- Receive Loop ----------------
    def _receive_loop(self):
        buffer = ""
        while self.running:
            try:
                data = self.sock.recv(4096)
                if not data:
                    print("[!] Server disconnected")
                    self.running = False
                    self.logged_in = False
                    self.user_id = None
                    break
                buffer += data.decode("utf-8")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line.strip():
                        try:
                            message = json.loads(line)
                            # Debug log
                            print("[<] Server:", message)

                            # Update login state if character_list received
                            if message.get("action") == "character_list":
                                self.logged_in = True
                                user = message.get("user")
                                if user:
                                    self.user_id = user.get("id")

                            self._response_queue.put(message)
                            if self.on_message:
                                self.on_message(message)
                        except Exception as e:
                            print(f"[!] Failed to parse server message: {line} - {e}")
            except Exception as e:
                print(f"[!] Receive error: {e}")
                self.running = False
                self.logged_in = False
                self.user_id = None
                break

    # ---------------- Send ----------------
    def send_json(self, data: dict):
        try:
            self.send(json.dumps(data))
        except Exception as e:
            print(f"[!] Failed to send JSON: {e}")

    def send(self, message: str):
        """Send raw string message, auto-reconnect if needed."""
        if not self.connected:
            try:
                self.connect()
                # Wait for login to complete if we had previous credentials
                if hasattr(self, "_last_login") and not self.logged_in:
                    # simple blocking wait for login to complete
                    start = time.time()
                    while not self.logged_in and time.time() - start < 5:
                        time.sleep(0.05)
                    if not self.logged_in:
                        print("[!] Cannot send: login did not complete")
                        return
            except Exception as e:
                print(f"[!] Cannot send: failed to reconnect: {e}")
                return
        try:
            self.sock.sendall((message + "\n").encode("utf-8"))
        except Exception as e:
            print(f"[!] Failed to send message: {e}")
            self.running = False
            self.sock.close()
            self.sock = None


    # ---------------- Login ----------------
    def login(self, username: str, password: str):
        self._last_login = (username, password)
        self.connect()  # ensures connection
        self.send_json({
            "action": "login",
            "data": {"username": username, "password": password}
        })
        # request(...) can still be used for blocking login if needed
        return self.request(expect_action="character_list")

    # ---------------- Request ----------------
    def request(self, data: dict = None, expect_action=None, timeout=5):
        """Send a JSON message and block until a matching response is received."""
        if data:
            self.send_json(data)
        try:
            start = time.time()
            while True:
                remaining = max(0, timeout - (time.time() - start))
                msg = self._response_queue.get(timeout=remaining)
                if expect_action is None or msg.get("action") == expect_action:
                    return msg
        except queue.Empty:
            print("[!] Request timed out")
            return None

    # ---------------- Character Management ----------------
    def delete_character(self, char_id):
        if not self.connected:
            print("[!] Cannot delete: client not connected")
            return None
        if not self.logged_in:
            print("[!] Cannot delete: user not logged in")
            return None
        return self.request(
            {"action": "delete_character", "data": {"char_id": char_id}},
            expect_action="delete_character_ok"
        )

    # ---------------- Close ----------------
    def close(self):
        self.running = False
        self.logged_in = False
        self.user_id = None
        if self.sock:
            self.sock.close()
            self.sock = None

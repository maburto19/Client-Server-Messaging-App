import json
import socket
import threading
import time
import uuid
import tkinter as tk
from datetime import datetime, timezone
from tkinter import ttk, messagebox


class EmbeddedDSServer:
    def __init__(self, log_callback, state_callback):
        self._log = log_callback
        self._state_callback = state_callback
        self._server_socket = None
        self._thread = None
        self._running = threading.Event()
        self._lock = threading.Lock()
        self.users = {}
        self.tokens = {}

    def start(self, host: str, port: int) -> None:
        if self._running.is_set():
            self._log("Server is already running.")
            return

        self._running.set()
        self._thread = threading.Thread(
            target=self._serve_forever, args=(host, port), daemon=True
        )
        self._thread.start()

    def stop(self) -> None:
        if not self._running.is_set():
            self._log("Server is not running.")
            return
        self._running.clear()
        if self._server_socket is not None:
            try:
                self._server_socket.close()
            except OSError:
                pass
        self._server_socket = None
        self._log("Server stopping...")

    def _serve_forever(self, host: str, port: int) -> None:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                self._server_socket = sock
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind((host, port))
                sock.listen()
                sock.settimeout(0.5)

                self._log(f"Local DS server listening on {host}:{port}")
                while self._running.is_set():
                    try:
                        conn, addr = sock.accept()
                        t = threading.Thread(
                            target=self._handle_client, args=(conn, addr), daemon=True
                        )
                        t.start()
                    except socket.timeout:
                        continue
                    except OSError:
                        break
        except OSError as e:
            self._log(f"Server failed to start: {e}")
        finally:
            self._running.clear()
            self._server_socket = None
            self._log("Server stopped.")

    def _handle_client(self, conn: socket.socket, addr) -> None:
        self._log(f"Connected: {addr}")
        conn.settimeout(10.0)
        buffer = ""
        try:
            with conn:
                while self._running.is_set():
                    try:
                        data = conn.recv(4096)
                    except socket.timeout:
                        continue
                    except OSError:
                        break
                        
                    if not data:
                        break
                    buffer += data.decode("utf-8", errors="replace")

                    while buffer:
                        buffer = buffer.lstrip()
                        if not buffer:
                            break
                        try:
                            obj, idx = json.JSONDecoder().raw_decode(buffer)
                            buffer = buffer[idx:]
                        except json.JSONDecodeError:
                            break

                        self._log(f"Received {addr}: {obj}")
                        response = self._process(obj)
                        resp_str = json.dumps(response) + "\n"
                        try:
                            conn.sendall(resp_str.encode("utf-8"))
                            self._log(f"Sent {addr}: {response}")
                            # Schedule UI update after sending response
                            self._state_callback()
                        except OSError:
                            break
        except Exception as e:
            self._log(f"Error handling {addr}: {e}")
        finally:
            self._log(f"Disconnected: {addr}")

    def _new_token(self) -> str:
        return "local_" + uuid.uuid4().hex

    def _process(self, obj: dict) -> dict:
        if "join" in obj:
            return self._join(obj["join"])
        if "post" in obj:
            return self._post(obj)
        if "bio" in obj:
            return self._bio(obj)
        return {"response": {"type": "error", "message": "Unknown request"}}

    def _join(self, join_obj: dict) -> dict:
        username = str(join_obj.get("username", "")).strip()
        password = str(join_obj.get("password", "")).strip()
        if not username or not password:
            return {"response": {"type": "error", "message": "Missing username or password"}}

        with self._lock:
            if username in self.users:
                if self.users[username]["password"] != password:
                    return {
                        "response": {
                            "type": "error",
                            "message": "Invalid password or username already taken",
                        }
                    }
                token = self._new_token()
                self.users[username]["token"] = token
                self.tokens[token] = username
                return {
                    "response": {
                        "type": "ok",
                        "message": "Welcome back!",
                        "token": token,
                    }
                }

            token = self._new_token()
            self.users[username] = {"password": password, "token": token, "bio": "", "posts": []}
            self.tokens[token] = username
            return {
                "response": {
                    "type": "ok",
                    "message": "Welcome to local DS server!",
                    "token": token,
                }
            }

    def _post(self, obj: dict) -> dict:
        token = obj.get("token", "")
        post_obj = obj.get("post", {})
        entry = str(post_obj.get("entry", ""))
        timestamp = post_obj.get("timestamp")
        if len(entry.strip()) == 0:
            return {"response": {"type": "error", "message": "Post cannot be empty"}}

        with self._lock:
            username = self.tokens.get(token)
            if username is None:
                return {"response": {"type": "error", "message": "Invalid or expired token"}}
            self.users[username]["posts"].append(
                {
                    "entry": entry,
                    "timestamp": timestamp,
                    "server_received_at": datetime.now(timezone.utc).isoformat(),
                }
            )
        return {"response": {"type": "ok", "message": "Post successfully received"}}

    def _bio(self, obj: dict) -> dict:
        token = obj.get("token", "")
        bio_obj = obj.get("bio", {})
        entry = str(bio_obj.get("entry", ""))
        with self._lock:
            username = self.tokens.get(token)
            if username is None:
                return {"response": {"type": "error", "message": "Invalid or expired token"}}
            self.users[username]["bio"] = entry
        return {"response": {"type": "ok", "message": "Bio successfully updated"}}

    def snapshot(self) -> str:
        with self._lock:
            return json.dumps(self.users, indent=2)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DS-Sandbox: Offline Distributed Social Protocol Tester")
        self.geometry("1100x700")

        self.server = EmbeddedDSServer(self.server_log, self.request_refresh_state)
        self.client_token = ""

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_ui(self):
        root = ttk.Frame(self, padding=10)
        root.pack(fill="both", expand=True)
        root.columnconfigure(0, weight=1)
        root.columnconfigure(1, weight=1)
        root.rowconfigure(1, weight=1)

        ttk.Label(root, text="Server", font=("Segoe UI", 12, "bold")).grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(root, text="Client", font=("Segoe UI", 12, "bold")).grid(
            row=0, column=1, sticky="w"
        )

        self._build_server_panel(root)
        self._build_client_panel(root)

    def _build_server_panel(self, root):
        panel = ttk.Frame(root, padding=(0, 5, 10, 0))
        panel.grid(row=1, column=0, sticky="nsew")
        panel.columnconfigure(1, weight=1)
        panel.rowconfigure(4, weight=1)
        panel.rowconfigure(6, weight=1)

        ttk.Label(panel, text="Host").grid(row=0, column=0, sticky="w")
        self.server_host = tk.StringVar(value="127.0.0.1")
        ttk.Entry(panel, textvariable=self.server_host).grid(row=0, column=1, sticky="ew")

        ttk.Label(panel, text="Port").grid(row=1, column=0, sticky="w")
        self.server_port = tk.StringVar(value="3021")
        ttk.Entry(panel, textvariable=self.server_port).grid(row=1, column=1, sticky="ew")

        btns = ttk.Frame(panel)
        btns.grid(row=2, column=0, columnspan=2, sticky="w", pady=8)
        ttk.Button(btns, text="Start Server", command=self.start_server).pack(side="left", padx=(0, 6))
        ttk.Button(btns, text="Stop Server", command=self.stop_server).pack(side="left", padx=(0, 6))
        ttk.Button(btns, text="Refresh State", command=self.refresh_state).pack(side="left")

        ttk.Label(panel, text="Server Log").grid(row=3, column=0, columnspan=2, sticky="w")
        self.server_log_box = tk.Text(panel, height=12, wrap="word")
        self.server_log_box.grid(row=4, column=0, columnspan=2, sticky="nsew")

        ttk.Label(panel, text="Server State (users, bios, posts)").grid(
            row=5, column=0, columnspan=2, sticky="w", pady=(8, 0)
        )
        self.state_box = tk.Text(panel, height=12, wrap="none")
        self.state_box.grid(row=6, column=0, columnspan=2, sticky="nsew")

    def _build_client_panel(self, root):
        panel = ttk.Frame(root, padding=(10, 5, 0, 0))
        panel.grid(row=1, column=1, sticky="nsew")
        panel.columnconfigure(1, weight=1)
        panel.rowconfigure(8, weight=1)

        ttk.Label(panel, text="Server Host").grid(row=0, column=0, sticky="w")
        self.client_host = tk.StringVar(value="127.0.0.1")
        ttk.Entry(panel, textvariable=self.client_host).grid(row=0, column=1, sticky="ew")

        ttk.Label(panel, text="Server Port").grid(row=1, column=0, sticky="w")
        self.client_port = tk.StringVar(value="3021")
        ttk.Entry(panel, textvariable=self.client_port).grid(row=1, column=1, sticky="ew")

        ttk.Label(panel, text="Username").grid(row=2, column=0, sticky="w")
        self.username = tk.StringVar(value="test1")
        ttk.Entry(panel, textvariable=self.username).grid(row=2, column=1, sticky="ew")

        ttk.Label(panel, text="Password").grid(row=3, column=0, sticky="w")
        self.password = tk.StringVar(value="test1")
        ttk.Entry(panel, textvariable=self.password, show="*").grid(row=3, column=1, sticky="ew")

        ttk.Label(panel, text="Post Message").grid(row=4, column=0, sticky="nw")
        self.post_text = tk.Text(panel, height=4, wrap="word")
        self.post_text.grid(row=4, column=1, sticky="ew")

        ttk.Label(panel, text="Bio").grid(row=5, column=0, sticky="nw")
        self.bio_text = tk.Text(panel, height=3, wrap="word")
        self.bio_text.grid(row=5, column=1, sticky="ew")

        self.token_var = tk.StringVar(value="(no token)")
        ttk.Label(panel, text="Token").grid(row=6, column=0, sticky="w")
        ttk.Label(panel, textvariable=self.token_var).grid(row=6, column=1, sticky="w")

        btns = ttk.Frame(panel)
        btns.grid(row=7, column=0, columnspan=2, sticky="w", pady=8)
        ttk.Button(btns, text="Join", command=self.join).pack(side="left", padx=(0, 6))
        ttk.Button(btns, text="Send Post", command=self.send_post).pack(side="left", padx=(0, 6))
        ttk.Button(btns, text="Update Bio", command=self.send_bio).pack(side="left", padx=(0, 6))
        ttk.Button(btns, text="Post + Bio", command=self.send_both).pack(side="left")

        ttk.Label(panel, text="Client Log").grid(row=8, column=0, columnspan=2, sticky="w")
        self.client_log_box = tk.Text(panel, height=18, wrap="word")
        self.client_log_box.grid(row=9, column=0, columnspan=2, sticky="nsew")
        panel.rowconfigure(9, weight=1)

    def _client_params(self):
        host = self.client_host.get().strip()
        port_text = self.client_port.get().strip()
        user = self.username.get().strip()
        pwd = self.password.get().strip()
        if not host or not port_text or not user or not pwd:
            raise ValueError("Host, port, username and password are required.")
        return host, int(port_text), user, pwd

    def _send_request(self, payload: dict) -> dict:
        host, port, _, _ = self._client_params()
        with socket.create_connection((host, port), timeout=10) as sock:
            sock.settimeout(10)
            data = (json.dumps(payload) + "\r\n").encode("utf-8")
            sock.sendall(data)
            # Removed sock.shutdown(socket.SHUT_WR) to avoid breaking some servers

            chunks = b""
            while True:
                try:
                    part = sock.recv(4096)
                except socket.timeout:
                    if chunks: break
                    raise
                if not part:
                    break
                chunks += part
                
                # Try to parse the current buffer; if it's a valid JSON, return it immediately
                try:
                    decoded = chunks.decode("utf-8", errors="replace").strip()
                    if decoded:
                        # If there are multiple lines (e.g. debugging info + json), 
                        # we look for the last line which is usually the JSON response
                        lines = [l.strip() for l in decoded.splitlines() if l.strip()]
                        for line in reversed(lines):
                            try:
                                return json.loads(line)
                            except json.JSONDecodeError:
                                continue
                except Exception:
                    continue
            
            if not chunks:
                return {"response": {"type": "error", "message": "No response from server"}}
            
            # Final fallback
            raw = chunks.decode("utf-8", errors="replace").strip()
            return json.loads(raw)

    def join(self):
        try:
            _, _, user, pwd = self._client_params()
            payload = {"join": {"username": user, "password": pwd, "token": ""}}
            self.client_log(f"Sending join: {payload}")
            resp = self._send_request(payload)
            self.client_log(f"Join response: {resp}")
            if resp.get("response", {}).get("type") == "ok":
                self.client_token = resp["response"].get("token", "")
                self.token_var.set(self.client_token or "(no token)")
            self.refresh_state()
        except Exception as e:
            self.client_log(f"Join failed: {e}")
            messagebox.showerror("Join failed", str(e), parent=self)

    def send_post(self):
        try:
            if not self.client_token:
                raise ValueError("Join first to receive a token.")
            entry = self.post_text.get("1.0", "end").strip()
            payload = {
                "token": self.client_token,
                "post": {"entry": entry, "timestamp": time.time()},
            }
            self.client_log(f"Sending post: {payload}")
            resp = self._send_request(payload)
            self.client_log(f"Post response: {resp}")
            self.refresh_state()
        except Exception as e:
            self.client_log(f"Post failed: {e}")
            messagebox.showerror("Post failed", str(e), parent=self)

    def send_bio(self):
        try:
            if not self.client_token:
                raise ValueError("Join first to receive a token.")
            entry = self.bio_text.get("1.0", "end").strip()
            payload = {
                "token": self.client_token,
                "bio": {"entry": entry, "timestamp": time.time()},
            }
            self.client_log(f"Sending bio: {payload}")
            resp = self._send_request(payload)
            self.client_log(f"Bio response: {resp}")
            self.refresh_state()
        except Exception as e:
            self.client_log(f"Bio failed: {e}")
            messagebox.showerror("Bio failed", str(e), parent=self)

    def send_both(self):
        self.send_post()
        self.send_bio()

    def start_server(self):
        try:
            host = self.server_host.get().strip()
            port = int(self.server_port.get().strip())
            self.server.start(host, port)
            # Keep client target aligned with currently configured local server.
            self.client_host.set(host)
            self.client_port.set(str(port))
        except Exception as e:
            messagebox.showerror("Server start failed", str(e), parent=self)

    def stop_server(self):
        self.server.stop()

    def refresh_state(self):
        state = self.server.snapshot()
        self.state_box.delete("1.0", "end")
        self.state_box.insert("end", state)

    def request_refresh_state(self):
        self.after(0, self.refresh_state)

    def server_log(self, message: str):
        self.after(0, self._append_server_log, message)

    def _append_server_log(self, message: str):
        self.server_log_box.insert("end", message + "\n")
        self.server_log_box.see("end")

    def client_log(self, message: str):
        self.client_log_box.insert("end", message + "\n")
        self.client_log_box.see("end")

    def on_close(self):
        self.server.stop()
        self.destroy()


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()

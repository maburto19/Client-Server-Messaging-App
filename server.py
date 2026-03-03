import json
import socket
import threading
import uuid
from datetime import datetime, timezone

# In-memory store for local development/testing.
USERS = {}   # username -> {"password": str, "token": str, "bio": str, "posts": list[dict]}
TOKENS = {}  # token -> username
LOCK = threading.Lock()

def _ok(message: str, token: str = None) -> dict:
    response = {"response": {"type": "ok", "message": message}}
    if token is not None:
        response["response"]["token"] = token
    return response

def _error(message: str) -> dict:
    return {"response": {"type": "error", "message": message}}

def _new_token() -> str:
    return f"local_{uuid.uuid4().hex}"

def _resolve_user_from_token(token: str) -> str | None:
    with LOCK:
        return TOKENS.get(token)

def _handle_join(obj: dict) -> dict:
    join_obj = obj.get("join", {})
    username = join_obj.get("username", "")
    password = join_obj.get("password", "")

    if not username or not password:
        return _error("Missing username or password")

    with LOCK:
        if username in USERS:
            # Existing user: must match password.
            if USERS[username]["password"] != password:
                return _error("Invalid password or username already taken")
            token = _new_token()
            USERS[username]["token"] = token
            TOKENS[token] = username
            return _ok("Welcome back!", token)

        # New user registration on first join.
        token = _new_token()
        USERS[username] = {
            "password": password,
            "token": token,
            "bio": "",
            "posts": [],
        }
        TOKENS[token] = username
        return _ok("Welcome to local DS server!", token)

def _handle_post(obj: dict) -> dict:
    # Client sends 'token' at top level, 'post' contains entry and timestamp
    token = obj.get("token", "")
    username = _resolve_user_from_token(token)
    if username is None:
        return _error("Invalid or expired token")

    post_obj = obj.get("post", {})
    entry = post_obj.get("entry", "")
    timestamp = post_obj.get("timestamp")

    if not isinstance(entry, str) or len(entry.strip()) == 0:
        return _error("Post cannot be empty")

    with LOCK:
        USERS[username]["posts"].append(
            {
                "entry": entry,
                "timestamp": timestamp,
                "server_received_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        post_count = len(USERS[username]["posts"])

    print(f"[post] user={username} total_posts={post_count} entry={entry!r}")
    return _ok("Post successfully received")

def _handle_bio(obj: dict) -> dict:
    # Client sends 'token' at top level, 'bio' contains entry
    token = obj.get("token", "")
    username = _resolve_user_from_token(token)
    if username is None:
        return _error("Invalid or expired token")

    bio_obj = obj.get("bio", {})
    entry = bio_obj.get("entry", "")

    if not isinstance(entry, str):
        return _error("Bio must be a string")

    with LOCK:
        USERS[username]["bio"] = entry

    print(f"[bio] user={username} bio={entry!r}")
    return _ok("Bio successfully updated")

def process_message(obj: dict) -> dict:
    if "join" in obj:
        return _handle_join(obj)
    # Check for keys in top level as per ds_protocol.py
    if "post" in obj:
        return _handle_post(obj)
    if "bio" in obj:
        return _handle_bio(obj)
    return _error("Unknown request")

def handle_client(conn, addr):
    print(f"[-] Connected by {addr}")
    # Set a timeout for individual socket operations
    conn.settimeout(10.0) 
    buffer = ""
    try:
        while True:
            try:
                data = conn.recv(4096).decode("utf-8")
            except socket.timeout:
                # If no data for 10s, just continue and try again
                continue
            
            if not data:
                break

            buffer += data

            # Parse one or more JSON objects from the incoming stream.
            while buffer:
                buffer = buffer.lstrip()
                if not buffer:
                    break

                try:
                    obj, idx = json.JSONDecoder().raw_decode(buffer)
                    buffer = buffer[idx:]
                    print(f"[<] Received from {addr}: {obj}")

                    response = process_message(obj)
                    # The newline \n is CRITICAL for connection.py readline()
                    resp_str = json.dumps(response) + "\n"
                    conn.sendall(resp_str.encode("utf-8"))
                    print(f"[>] Sent to {addr}: {resp_str.strip()}")
                except json.JSONDecodeError:
                    # Incomplete JSON payload; wait for more bytes.
                    break
    except Exception as e:
        print(f"[!] Error handling {addr}: {e}")
    finally:
        conn.close()
        print(f"[-] Disconnected {addr}")

def start_server(host="127.0.0.1", port=3021):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind to localhost specifically to avoid firewall issues
        sock.bind((host, port))
        sock.listen()

        print(f"[*] Local DS server listening on {host}:{port}")
        print("[*] Use Ctrl+C to stop.\n")

        try:
            while True:
                conn, addr = sock.accept()
                thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
                thread.start()
        except KeyboardInterrupt:
            print("\n[*] Shutting down local DS server.")

if __name__ == "__main__":
    start_server()

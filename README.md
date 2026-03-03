# DS-Sandbox: Offline Distributed Social Protocol Tester

This project is a development and testing environment for the **Distributed Social (DS) Protocol**. It includes a full client implementation, a command-line interface (CLI), and a "Sandbox" GUI that allows you to run a local server and test your code entirely offline. However, the server needs to run in the terminal for it to work.

---

## How to Run

### To run GUI
This is the easiest way to test your protocol logic without needing an internet connection.
1. Run the terminal: "py server.py" to start the server, and then run the GUI: python local_ds_gui.py 
2. Click **"Start Server"** on the left panel.
3. Use the right panel to **Join**, **Post**, or **Update Bio**.
4. Watch the "Server State" box update in real-time as your client sends data.

### To run only on therminal
To run the main assignment client:
1. First, start the standalone server in its own terminal: python server.py

2. In a second terminal, run the client: python a4.py
 
3. When prompted for a server IP, use `127.0.0.1` and port `3021`.

---


## Protocol Details
The server and client communicate using JSON-formatted strings. Every message must be terminated by a newline (`
`).

**Example Join Request:**
```json
{"join": {"username": "user", "password": "pw", "token": ""}}
```

**Example Response:**
```json
{"response": {"type": "ok", "message": "Welcome!", "token": "unique_token_here"}}
```

---

## Author
**MIA DESIREE ABURTO**  
*MABURTO@UCI.EDU*

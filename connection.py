'''Module which establishes connection to server'''
from collections import namedtuple
import socket
import json


def init(sock):
    '''makes tuple of the initial connection'''
    Connection = namedtuple('connect', ['sock', 'send', 'recv'])
    try:
        send = sock.makefile('w')
        recv = sock.makefile('r')
    except (socket.error, socket.timeout,
            socket.herror, socket.gaierror,
            ConnectionError) as e:
        if isinstance(e, ConnectionError):
            print(f"Connection error: {e}")
        else:
            print(f"Socket error: {e}")

    connect = Connection(sock, send, recv)
    return connect


def connect_server(host, port):
    '''connects to server'''
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        return sock
    except (ConnectionError, socket.timeout, socket.herror,
            socket.gaierror) as e:
        print(f"Error: {e}")
        return None


def send_server(connection: tuple, join_string: str) -> bool:
    '''senf information to server'''
    try:
        # DS protocol servers read one JSON message per line.
        connection.send.write(join_string + '\r\n')
        connection.send.flush()
        resp = connection.recv.readline()[:-1]
        resp = json.loads(resp)
        return resp
    except (ConnectionError, socket.timeout, socket.herror,
            socket.gaierror) as e:
        print(f"Error: {e}")
        return None


def disconnect(test_c):
    '''disconnects server'''
    test_c.send.close()
    test_c.recv.close()

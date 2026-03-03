'''ds client module send info to server'''
# Replace the following placeholders with your information.

# MIA DESIREE ABURTO
# MABURTO@UCI.EDU
# 12216719

import json
import ds_protocol as protocol
import connection as conn

# server_address = 168.235.86.101
# server_port = 3021

ERROR_MESSAGE = "Error: Not able to connect to server"
CONNECTION = "Server connected succesfully!"
COMMAND = "What would you like to do? \n(Q) Quit\n(J)Join"
SUCCESS = 'Success! It works'


def send(server: str, port: int, username: str, password: str, message: str, bio: str = None):
    '''
    The send function joins a ds server and sends a message, bio, or both

    :param server: The ip address for the ICS 32 DS server.
    :param port: The port where the ICS 32 DS server is accepting connections.
    :param username: The user name to be assigned to the message.
    :param password: The password associated with the username.
    :param message: The message to be sent to the server.
    :param bio: Optional, a bio for the user.
    '''

    def error_handling(error):
        print(error)
        return False

    if not check_empty(server) or not check_empty(str(port)):
        return error_handling('Empty server or port')

    sock = conn.connect_server(server, port)
    if sock is None:
        print(ERROR_MESSAGE)
        return False

    print(CONNECTION)
    tuple_c = conn.init(sock)

    obj = protocol.ClientProtocol(password, username)
    resp = join(username, password, tuple_c, obj)

    if resp is False or tuple_c is False:
        return error_handling('Not able to join')

    token = resp['response'].get('token')
    lenm = len(message)

    if lenm == 0 and not bio:
        print('Error: Need more information')
        return False

    return last_step(bio, message, token, tuple_c, obj)


def last_step(bio, message, token, tuple_c, obj):
    '''error handling'''
    error_occured = False
    lenm = len(message)

    if lenm != 0 and bio:
        if not check_empty(message) or not check_empty(bio):
            print('Error: empty post or bio')
            return False
        resp = do_bio(token, bio, tuple_c, obj)
        resp2 = do_post(token, message, tuple_c, obj)
        if (resp is False or resp2 is False):
            error_occured = True

    if lenm != 0 and bio is None:
        if not check_empty(message):
            print('ERROR EMPTY POST')
            return False
        resp = do_post(token, message, tuple_c, obj)
        if resp is False:
            error_occured = True

    if bio is not None:
        if not check_empty(bio):
            print('ERROR EMPTY POST')
            return False
        resp = do_bio(token, bio, tuple_c, obj)
        if resp is False:
            error_occured = True
    if error_occured:
        return False
    return True


def check_empty(var) -> bool:
    '''checks spaces or if it is empty'''
    string = str(var)
    if len(string.strip()) == 0:
        return False
    return True


def check_response(resp: dict) -> bool:
    '''returns false if an error occured'''
    if resp['response']['type'] == 'error':
        return False
    return True


def do_post(token, post, connection, prot) -> bool:
    '''sends post to server'''
    json_post = prot.create_post(post, token)
    print('>>> Message posted', json_post)
    post_string = json.dumps(json_post)
    resp = conn.send_server(connection, post_string)
    print('>>> Server response', resp)
    print(resp)
    b = check_response(resp)
    if b is False:
        return False
    return True


def do_bio(token, bio, connection, prot) -> bool:
    '''sends bio to server'''
    json_bio = prot.create_bio(bio, token)
    bio_string = json.dumps(json_bio)
    resp = conn.send_server(connection, bio_string)
    print('>>> Server response:', resp)
    b = check_response(resp)
    if b is False:
        return False
    return True


def join(new_username, new_password, connection, prot):
    '''allows the user to join the server'''
    try:
        json_join = prot.create_join(new_username, new_password)
        print('>>>', json_join)
        join_string = json.dumps(json_join)
        resp = conn.send_server(connection, join_string)
        print('>>> Server response:', resp)
        b = check_response(resp)
        if b is False:
            return False
        return resp
    except ConnectionError:
        print('Connection Error')
        return False
    except TimeoutError:
        print('Timeout Error')
        return False

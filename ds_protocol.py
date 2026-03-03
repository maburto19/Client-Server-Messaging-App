'''Protocol module: formats the information
to adhere the server protocol constraints'''
# ds_protocol.py

# Replace the following placeholders with your information.

# MIA DESIREE ABURTO
# MABURTO@UCI.EDU
# 12216719

import json
from collections import namedtuple
import time

# Namedtuple to hold the values retrieved from json messages.
DataTuple = namedtuple(
    'DataTuple', ['join', 'token', 'bio', 'post', 'response'])


class ServerError(Exception):
    '''Exception when there is a server error'''


def extract_json(json_msg: str) -> DataTuple:
    '''Data tuple'''
    try:
        json_obj = json.loads(json_msg)
        join = json_obj.get("join")
        post = json_obj.get("post")
        bio = json_obj.get("bio")
        response = json_obj.get("response")
        token = None
        if isinstance(response, dict):
            token = response.get("token")
        elif isinstance(join, dict):
            token = join.get("token")
    except json.JSONDecodeError:
        print("Json cannot be decoded.")
        return DataTuple(None, None, None, None, None)

    return DataTuple(join, token, bio, post, response)


class ClientProtocol:
    '''class to forma the client protocol'''
    def __init__(self, pwd, user) -> None:
        '''initialize the values'''

        self.pwd = pwd
        self.user = user

    def create_join(self, user, pwd):
        '''formats the join to send'''
        join_dict = {
            'join': {
                'username': user,
                'password': pwd,
                'token': ''
            }
        }
        return join_dict

    def create_post(self, message, token):
        '''formats the post to send'''
        timestamp = time.time()
        post_dict = {
            'token': token,
            'post':
            {
                'entry': message,
                'timestamp': timestamp
            }
        }

        return post_dict

    def create_bio(self, bio, token):
        '''formats the bio to send'''
        times = time.time()
        bio_dict = {
            'token': token,
            'bio': {
                'entry': bio,
                'timestamp': times

            }
        }
        return bio_dict

'''Module for the music API'''
# openMusic.py

# Starter code for assignment 4 in ICS 32
# Programming with Software Libraries in Python

# Replace the following placeholders with your information.

# MIA DESIREE ABURTO
# MABURTO@UCI.EDU
# 12216719

import urllib
import json
from urllib import request, error
import WebAPI as w


class LastFM(w.WebAPI):
    '''class OPEN MUSIC'''

    def __init__(self, artist='Lady Gaga'):
        '''Initiialize'''
        super().__init__()
        self.artist = self.set_artist(artist)
        self.apikey = None
        self.url = None
        self.tracks = None
        # creates required class attribute apikey
        # creates API specific class attributes like zip, ccode

    def load_data(self):
        '''djafjsd'''
        try:
            domain = 'https://ws.audioscrobbler.com/2.0/'
            si = '?method=artist.gettoptracks&'
            last = f"{self.artist}&api_key={self.apikey}"
            url = f"{domain}{si}artist={last}&format=json"
            music_obj = self._download_url(url)
            if not isinstance(music_obj, dict):
                return False
            if 'error' in music_obj:
                print(music_obj.get('message', 'Unknown LastFM error'))
                return False
            return music_obj
        except TypeError as e:
            print('>>> Type Error:', e)
            return False
        except ValueError as e:
            print('>>> Value error:', e)
            return False


    def transclude(self, message: str) -> str:
        '''jiaesf'''
        transcluded = message.split()
        post = ''
        for word in transcluded:
            if word == '@lastfm':
                word = self.url['toptracks']['track'][0]['name']
            post += word
            post += ' '
        return post

    def set_artist(self, artist):
        '''uafdadu'''
        artist = artist.strip()
        if len(artist) == 0:
            print('Empty')
        artist = artist.replace(' ', '+')
        return artist
    



def main():
    '''ejadgjad'''
    artist = input('Enter artist name: ')
    apikey = input('Enter API KEY: ')
    music_obj = LastFM(artist)
    music_obj.set_apikey(apikey)
    music_obj.load_data()

    # 90255
    if music_obj is not None:
        pass
        # print(music_obj.url['weather'][0]['description'])
    print(music_obj.transclude('today is @lastfm jajajaj'))

    # 'WEATHER KEY: 51c14ef187e0c51311a07d728ea27b5b'
    # 'openMusic KEY: 2123271d41900e1de08ff50a71db2d3f'

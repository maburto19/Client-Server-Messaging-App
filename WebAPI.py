'''safdsgfhdgj'''
# webapi.py

# Starter code for assignment 4 in ICS 32
# Programming with Software Libraries in Python

# Replace the following placeholders with your information.

# NAME
# EMAIL
# STUDENT ID

from abc import ABC, abstractmethod
from urllib import request, error
import urllib
import json


class Error404(Exception):
    '''Raise exception'''


class ConnError(Exception):
    '''Connection error'''


class Error503(Exception):
    '''Raise exception'''


class HTTPError(Exception):
    '''Raise exception'''


class UrlError(Exception):
    '''Url and connecion error'''


class JSONError(Exception):
    '''Json error class'''


class WebAPI(ABC):
    '''afegsrhd'''

    def __init__(self):
        self.url = None
        self.apikey = None

    def _download_url(self, url: str) -> dict:
        '''jafesdgd'''
        response = None
        r_obj = None

        try:
            with urllib.request.urlopen(url) as response:
                json_results = response.read()
                r_obj = json.loads(json_results)
                self.url = r_obj

        except urllib.error.HTTPError as e:
            print('Failed to download contents of URL')
            print(f'Status code: {e.code}')
            if e.code == 404:
                try:
                    raise Error404 from e
                except Error404:
                    me = '>>> HTTP Error 404: Remote API'
                    print(me + ' is unavailable, resource could not be found.')
            elif e.code == 503:
                try:
                    raise Error503 from e
                except Error503:
                    me = '>>> HTTP Error 503: Service unavailable'
                    print(me + '. The remote API is currently unavailable.')
            else:
                try:
                    raise HTTPError from e
                except HTTPError:
                    m = f"'>>> HTTP Error {e.code}: An "
                    print(m, 'unexpected HTTP error occurred.')

        except urllib.error.URLError as e:
            try:
                raise UrlError from e
            except UrlError:
                m = '>>> Lost Connection/URL Error: Failed to'
                print(m, f'reach the server. {e.reason}')

        except json.JSONDecodeError as e:
            try:
                raise JSONError from e
            except JSONError:
                print(
                    f'>>> JSON Decode Error: Failed to parse JSON data. Error: {e}')

        except ConnectionError as e:
            try:
                raise ConnError from e
            except ConnError:
                print('>>> Connection error:', e)

        finally:
            if response is not None:
                response.close()

        return r_obj

    def set_apikey(self, apikey: str) -> None:
        '''afegsrdthjf'''
        self.apikey = apikey
        return self.apikey

    @abstractmethod
    def load_data(self):
        '''aegrsth'''

    @abstractmethod
    def transclude(self, message: str) -> str:
        '''afgdsfhdt'''

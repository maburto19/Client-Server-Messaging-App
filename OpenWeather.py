'''Module open weather'''
# openweather.py

# Starter code for assignment 4 in ICS 32
# Programming with Software Libraries in Python

# Replace the following placeholders with your information.

# NAME
# EMAIL
# STUDENT ID

import urllib
from urllib import request, error
import json
import WebAPI as w



class OpenWeather(w.WebAPI):
    '''class openweahter'''
    def __init__(self, _zip='92697', ccode='us'):
        '''Initiialize'''
        super().__init__()
        self._zip = _zip
        self.ccode = ccode
        self.url = None
        self.temperature = None
        self.high_temperature = None
        self.low_temperature = None
        self.longitude = None
        self.latitude = None
        self.description = None
        self.humidity = None
        self.sunset = None
        self.city = None


    def load_data(self):
        '''djafjsd'''
        domain = 'http://api.openweathermap.org/data/2.5/weather?'

        url = f"{domain}zip={self._zip},{self.ccode}&appid={self.apikey}"
        weather_obj = self._download_url(url)
        
        if not weather_obj or weather_obj is False:
            return False

        try:
            self.temperature = weather_obj['main']['temp']
            self.high_temperature = weather_obj['main']['temp_max']
            self.low_temperature = weather_obj['main']['temp_min']
            self.longitude = weather_obj['coord']['lon']
            self.latitude = weather_obj['coord']['lat']
            self.description = weather_obj['weather'][0]['description']
            self.humidity = weather_obj['main']['humidity']
            self.sunset = weather_obj['sys']['sunset']
            self.city = weather_obj['name']
            return weather_obj
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
            if word == '@weather':
                word = self.url['weather'][0]['description']
            post += word
            post += ' '
        return post

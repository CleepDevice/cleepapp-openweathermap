import unittest
import logging
import sys
sys.path.append('../')
from backend.openweathermap import Openweathermap
from raspiot.utils import InvalidParameter, MissingParameter, CommandError, Unauthorized
from raspiot.libs.tests import session
import os
import re
from backend.owmToDisplayAddOrReplaceMessageFormatter import OwmToDisplayAddOrReplaceMessageFormatter
from raspiot.profiles.displayAddOrReplaceMessageProfile import DisplayAddOrReplaceMessageProfile

class TestOpenweathermap(unittest.TestCase):

    FORECAST_SAMPLE = [
        {
            "clouds": {"all": 67},
            "sys": {"pod": "n"},
            "dt_txt": "2019-04-29 21:00:00",
            "weather": [{"main": "Clouds","id": 803,"icon": "04n","description": "broken clouds"}],"dt": 1556571600,
            "main": {"temp_kf": -0.27,"temp": 9.47,"grnd_level": 1018.03,"temp_max": 9.75,"sea_level": 1024.53,"humidity": 90,"pressure": 1024.53,"temp_min": 9.47},
            "wind": {"speed": 2.78,"deg": 57.579}
        },
        {
            "clouds": {"all": 44},
            "sys": {"pod": "n"},
            "dt_txt": "2019-04-30 00:00:00",
            "weather": [{"main": "Clouds","id": 802,"icon": "03n","description": "scattered clouds"}],
            "dt": 1556582400,
            "main": {"temp_kf": -0.2,"temp": 7.96,"grnd_level": 1018.23,"temp_max": 8.16,"sea_level": 1024.65,"humidity": 91,"pressure": 1024.65,"temp_min": 7.96},
            "wind": {"speed": 2.6,"deg": 119.66}
        },
        {
            "clouds": {"all": 47},
            "sys": {"pod": "n"},
            "dt_txt": "2019-04-30 03:00:00",
            "weather": [{"main": "Clouds","id": 802,"icon": "03n","description": "scattered clouds"}],
            "dt": 1556593200,
            "main": {"temp_kf": -0.14,"temp": 6.77,"grnd_level": 1017.06,"temp_max": 6.9,"sea_level": 1023.54,"humidity": 91,"pressure": 1023.54,"temp_min": 6.77},
            "wind": {"speed": 2.66,"deg": 138.261}
        },
        {
            "clouds": {"all": 48},
            "sys": {"pod": "d"},
            "dt_txt": "2019-04-30 06:00:00",
            "weather": [{"main": "Clouds","id": 802,"icon": "03d","description": "scattered clouds"}],
            "dt": 1556604000,
            "main": {"temp_kf": -0.07,"temp": 7.29,"grnd_level": 1017.71,"temp_max": 7.36,"sea_level": 1023.92,"humidity": 89,"pressure": 1023.92,"temp_min": 7.29},
            "wind": {"speed": 1.85,"deg": 162.742}
        },
        {
            "clouds": {"all": 29},
            "sys": {"pod": "d"},
            "dt_txt": "2019-04-30 09:00:00",
            "weather": [{"main": "Clouds","id": 802,"icon": "03d","description": "scattered clouds"}],
            "dt": 1556614800,
            "main": {"temp_kf": 0,"temp": 13.35,"grnd_level": 1017.89,"temp_max": 13.35,"sea_level": 1024.23,"humidity": 70,"pressure": 1024.23,"temp_min": 13.35},
            "wind": {"speed": 1.35,"deg": 128.11}
        },
        {
            "clouds": {"all": 41},
            "sys": {"pod": "d"},
            "dt_txt": "2019-04-30 12:00:00",
            "weather": [{"main": "Clouds","id": 802,"icon": "03d","description": "scattered clouds"}],
            "dt": 1556625600,
            "main": {"temp_kf": 0,"temp": 15.94,"grnd_level": 1016.91,"temp_max": 15.94,"sea_level": 1023.21,"humidity": 60,"pressure": 1023.21,"temp_min": 15.94},
            "wind": {"speed": 1.77,"deg": 31.108}
        },
        {
            "clouds": {"all": 83},
            "sys": {"pod": "d"},
            "dt_txt": "2019-04-30 15:00:00",
            "weather": [{"main": "Clouds","id": 803,"icon": "04d","description": "broken clouds"}],
            "dt": 1556636400,
            "main": {"temp_kf": 0,"temp": 16.15,"grnd_level": 1015.67,"temp_max": 16.15,"sea_level": 1021.92,"humidity": 65,"pressure": 1021.92,"temp_min": 16.15},
            "wind": {"speed": 3.52,"deg": 4.19}
        },
        {
            "clouds": {"all": 91},
            "sys": {"pod": "d"},
            "dt_txt": "2019-04-30 18:00:00",
            "weather": [{"main": "Clouds","id": 804,"icon": "04d","description": "overcast clouds"}],
            "dt": 1556647200,
            "main": {"temp_kf": 0,"temp": 13.15,"grnd_level": 1014.86,"temp_max": 13.15,"sea_level": 1021.06,"humidity": 78,"pressure": 1021.06,"temp_min": 13.15},
            "wind": {"speed": 3.91,"deg": 8.777}
        },
        {
            "clouds": {"all": 81},
            "sys": {"pod": "n"},
            "dt_txt": "2019-04-30 21:00:00",
            "weather": [{"main": "Clouds","id": 803,"icon": "04n","description": "broken clouds"}],
            "dt": 1556658000,
            "main": {"temp_kf": 0,"temp": 10.35,"grnd_level": 1014.85,"temp_max": 10.35,"sea_level": 1021.43,"humidity": 91,"pressure": 1021.43,"temp_min": 10.35},
            "wind": {"speed": 2.94,"deg": 51.088}
        },
        {
            "clouds": {"all": 91},
            "sys": {"pod": "n"},
            "dt_txt": "2019-05-01 00:00:00",
            "weather": [{"main": "Clouds","id": 804,"icon": "04n","description": "overcast clouds"}],
            "dt": 1556668800,
            "main": {"temp_kf": 0,"temp": 9.31,"grnd_level": 1013.91,"temp_max": 9.31,"sea_level": 1020.37,"humidity": 93,"pressure": 1020.37,"temp_min": 9.31},
            "wind": {"speed": 2.22,"deg": 91.495}
        }
    ]
    WEATHER_SAMPLE = {
        "clouds": {"all": 0},
        "name": "Rennes",
        "visibility": 10000,
        "sys": {"country": "FR","sunset": 1556565352,"message": 0.0054,"type": 1,"id": 6565,"sunrise": 1556513532},
        "weather": [{"main": "Clear","id": 800,"icon": "01n","description": "clear sky"}],
        "coord": {"lat": 48.12,"lon": -1.69},
        "base": "stations",
        "dt": 1556568424,
        "main": {"pressure": 1023,"temp_min": 9.44,"temp_max": 13,"temp": 11.23,"humidity": 71},
        "id": 6432801,
        "wind": {"speed": 3.1,"deg": 20},
        "cod": 200
    }

    def setUp(self):
        self.session = session.TestSession(logging.CRITICAL)
        logging.basicConfig(level=logging.CRITICAL, format=u'%(asctime)s %(name)s:%(lineno)d %(levelname)s : %(message)s')
        self.module = self.session.setup(Openweathermap)
        self.module._get_config = self.__get_config
        self.original_get_weather = self.module._get_weather
        self.original_get_forecast = self.module._get_forecast
        self.module._get_weather = lambda api: self.WEATHER_SAMPLE
        self.module._get_forecast = lambda api: self.FORECAST_SAMPLE
        self.api = self.get_api_key()

    def tearDown(self):
        self.session.clean()

    def get_api_key(self):
        if u'OWM_API_KEY' not in os.environ:
            raise Exception('Please set OWM_API_KEY environment variable')
        return os.environ['OWM_API_KEY']

    def test_get_weather_ok(self):
        """test real owm api response"""
        self.session.mock_command('get_position', self.__get_position)
        self.module._get_weather = self.original_get_weather
        resp = self.module._get_weather(self.api)
        self.assertTrue(isinstance(resp, dict), 'get_weather response should be dict')
        self.assertTrue('name' in resp, 'Response should contains "name" field')
        self.assertEqual(resp['name'], 'Rennes', 'City name should be Rennes')
        self.assertTrue('main' in resp, 'Response should contains "main" field')
        self.assertTrue('wind' in resp, 'Response should contains "wind" field')
        self.assertTrue('weather' in resp, 'Response should contains "weather" field')
        self.assertTrue('cod' in resp, 'Response should contains "cod" field')

    def test_get_weather_no_api(self):
        self.module._get_weather = self.original_get_weather
        with self.assertRaises(MissingParameter) as cm:
            self.module._get_weather(None)
        self.assertEqual(cm.exception.message, 'Parameter "apikey" is missing', 'Should raise error when api key is None')
        with self.assertRaises(MissingParameter) as cm:
            self.module._get_weather('')
        self.assertEqual(cm.exception.message, 'Parameter "apikey" is missing', 'Should raise error when api key is empty')

    def test_get_weather_get_position_failed(self):
        self.module._get_weather = self.original_get_weather
        self.session.mock_command('get_position', self.__get_position, fail=True)
        with self.assertRaises(CommandError) as cm:
            self.module._get_weather(self.api)
        self.assertEqual(cm.exception.message, 'TEST: command fails for tests', 'Invalid message when get_position failed')

        self.session.mock_command('get_position', self.__get_position, fail=False, no_response=True)
        with self.assertRaises(CommandError) as cm:
            self.module._get_weather(self.api)
        self.assertEqual(cm.exception.message, 'No response from parameters module', 'Invalid message when get_position returns None')

    def test_get_forecast_ok(self):
        """test real owm api response"""
        self.session.mock_command('get_position', self.__get_position)
        self.module._get_forecast = self.original_get_forecast
        resp = self.module._get_forecast(self.api)
        self.assertTrue(isinstance(resp, list), 'get_forecast response should be list')
        self.assertTrue(len(resp)>0, 'It should have forecast data')

    def test_get_forecast_no_api(self):
        self.module._get_forecast = self.original_get_forecast
        with self.assertRaises(MissingParameter) as cm:
            self.module._get_forecast(None)
        self.assertEqual(cm.exception.message, 'Parameter "apikey" is missing', 'Should raise error when api key is None')
        with self.assertRaises(MissingParameter) as cm:
            self.module._get_forecast('')
        self.assertEqual(cm.exception.message, 'Parameter "apikey" is missing', 'Should raise error when api key is empty')

    def test_get_forecast_get_position_failed(self):
        self.module._get_forecast = self.original_get_forecast
        self.session.mock_command('get_position', self.__get_position, fail=True)
        with self.assertRaises(CommandError) as cm:
            self.module._get_forecast(self.api)
        self.assertEqual(cm.exception.message, 'TEST: command fails for tests', 'Invalid message when get_position failed')

        self.session.mock_command('get_position', self.__get_position, fail=False, no_response=True)
        with self.assertRaises(CommandError) as cm:
            self.module._get_forecast(self.api)
        self.assertEqual(cm.exception.message, 'No response from parameters module', 'Invalid message when get_position returns None')

    def test_weather_task_ok(self):
        uuid = self.module.get_module_devices().keys()[0]
        
        calls = self.session.get_event_calls('openweathermap.weather.update')
        self.module._weather_task()
        device = self.module.get_module_devices()[uuid]
        self.assertEqual(device['code'], self.WEATHER_SAMPLE['weather'][0]['id'], 'code value is invalid')
        self.assertEqual(device['winddegrees'], self.WEATHER_SAMPLE['wind']['deg'], 'winddegrees value is invalid')
        self.assertTrue('winddirection' in device, 'winddirection value is missing')
        self.assertEqual(device['windspeed'], self.WEATHER_SAMPLE['wind']['speed'], 'windspeed value is invalid')
        self.assertEqual(device['celsius'], self.WEATHER_SAMPLE['main']['temp'], 'celsius value is invalid')
        self.assertTrue('fahrenheit' in device, 'fahrenheit value is missing')
        self.assertEqual(device['condition'].lower(), self.WEATHER_SAMPLE['weather'][0]['description'].lower(), 'condition value is invalid')
        self.assertIsNotNone(re.search(self.WEATHER_SAMPLE['weather'][0]['icon'], device['icon']), 'icon value is invalid')
        self.assertEqual(device['humidity'], self.WEATHER_SAMPLE['main']['humidity'], 'humidity value is invalid')
        self.assertEqual(device['pressure'], self.WEATHER_SAMPLE['main']['pressure'], 'pressure value is invalid')
        self.assertEqual(self.session.get_event_calls('openweathermap.weather.update'), calls+1, '"openweathermap.weather.update" wasn\'t triggered')

    def test_get_forecast(self):
        #weather task fill forecast
        self.module._weather_task()

        forecast = self.module.get_forecast()
        self.assertTrue(isinstance(forecast, list), 'forecast must be a list')
        self.assertEqual(len(forecast), len(self.FORECAST_SAMPLE), 'forecast content is invalid')

    def test_get_forecast_owm_failed(self):
        self.session.mock_command('get_position', self.__get_position)
        self.module._get_forecast = self.original_get_forecast

        self.module._owm_request = lambda u,d: (201, 'invaliddata')
        with self.assertRaises(Exception) as cm:
            self.module._get_forecast('apikey')
        self.assertEqual(cm.exception.message, 'Error requesting openweathermap api [201]', 'Status not 200 should be handled')

        self.module._owm_request = lambda u,d: (200, {'invaliddata'})
        with self.assertRaises(Exception) as cm:
            self.module._get_forecast('apikey')
        self.assertEqual(cm.exception.message, 'Invalid OWM api response format. Is API changed?', 'Bad response not properly handled')

        self.module._owm_request = lambda u,d: (200, {'cod': 201})
        with self.assertRaises(Exception) as cm:
            self.module._get_forecast('apikey')
        self.assertEqual(cm.exception.message, 'Unknown error', 'Unknown received data is not properly handled')

        self.module._owm_request = lambda u,d: (200, {'cod': 201, 'message':'TEST: owm error'})
        with self.assertRaises(Exception) as cm:
            self.module._get_forecast('apikey')
        self.assertEqual(cm.exception.message, 'TEST: owm error', 'Specific OWM error is not properly handled')

    def test_get_weather(self):
        #weather task fill weather
        self.module._weather_task()

        weather = self.module.get_weather()
        self.assertEqual(weather['code'], self.WEATHER_SAMPLE['weather'][0]['id'], 'code value is invalid')
        self.assertEqual(weather['winddegrees'], self.WEATHER_SAMPLE['wind']['deg'], 'winddegrees value is invalid')
        self.assertTrue('winddirection' in weather, 'winddirection value is missing')
        self.assertEqual(weather['windspeed'], self.WEATHER_SAMPLE['wind']['speed'], 'windspeed value is invalid')
        self.assertEqual(weather['celsius'], self.WEATHER_SAMPLE['main']['temp'], 'celsius value is invalid')
        self.assertTrue('fahrenheit' in weather, 'fahrenheit value is missing')
        self.assertEqual(weather['condition'].lower(), self.WEATHER_SAMPLE['weather'][0]['description'].lower(), 'condition value is invalid')
        self.assertIsNotNone(re.search(self.WEATHER_SAMPLE['weather'][0]['icon'], weather['icon']), 'icon value is invalid')
        self.assertEqual(weather['humidity'], self.WEATHER_SAMPLE['main']['humidity'], 'humidity value is invalid')
        self.assertEqual(weather['pressure'], self.WEATHER_SAMPLE['main']['pressure'], 'pressure value is invalid')

    def test_get_weather_owm_failed(self):
        self.session.mock_command('get_position', self.__get_position)
        self.module._get_weather = self.original_get_weather

        self.module._owm_request = lambda u,d: (201, 'invaliddata')
        with self.assertRaises(Exception) as cm:
            self.module._get_weather('apikey')
        self.assertEqual(cm.exception.message, 'Error requesting openweathermap api [201]', 'Status not 200 should be handled')

        self.module._owm_request = lambda u,d: (200, {'invaliddata'})
        with self.assertRaises(Exception) as cm:
            self.module._get_weather('apikey')
        self.assertEqual(cm.exception.message, 'Invalid OWM api response format. Is API changed?', 'Bad response not properly handled')

        self.module._owm_request = lambda u,d: (200, {'cod': 201})
        with self.assertRaises(Exception) as cm:
            self.module._get_weather('apikey')
        self.assertEqual(cm.exception.message, 'Unknown error', 'Unknown received data is not properly handled')

        self.module._owm_request = lambda u,d: (200, {'cod': 201, 'message':'TEST: owm error'})
        with self.assertRaises(Exception) as cm:
            self.module._get_weather('apikey')
        self.assertEqual(cm.exception.message, 'TEST: owm error', 'Specific OWM error is not properly handled')

    def test_set_apikey_valid(self):
        """this test request real owm api"""
        self.session.mock_command('get_position', self.__get_position)
        self.module._get_weather = self.original_get_weather
        self.assertTrue(self.module.set_apikey(self.api))

    def test_set_apikey_invalid(self):
        """this test request real owm api"""
        self.session.mock_command('get_position', self.__get_position)
        self.module._get_weather = self.original_get_weather
        with self.assertRaises(Exception) as cm:
            self.module.set_apikey('theapikey')
        self.assertEqual(cm.exception.message, 'Invalid OWM api key')

    def test_set_apikey_invalid_param(self):
        with self.assertRaises(MissingParameter) as cm:
            self.module.set_apikey(None)
        self.assertEqual(cm.exception.message, 'Parameter "apikey" is missing')

        with self.assertRaises(MissingParameter) as cm:
            self.module.set_apikey('')
        self.assertEqual(cm.exception.message, 'Parameter "apikey" is missing')

    
    def __get_config(self):
        return {
            'apikey': 'xxxxx'
        }

    def __get_position(self):
        return {
            'error': False,
            'data': {
                'latitude': 48.1159,
                'longitude': -1.6883,
            }
        }





class TestOwmToDisplayAddOrReplaceMessageFormatter(unittest.TestCase):
    def setUp(self):
        self.session = session.TestSession(logging.CRITICAL)
        logging.basicConfig(level=logging.CRITICAL, format=u'%(asctime)s %(name)s:%(lineno)d %(levelname)s : %(message)s')
        self.formatter = OwmToDisplayAddOrReplaceMessageFormatter(self.session.bootstrap['events_broker'])

    def tearDown(self):
        self.session.clean()

    def test_fill_profile(self):
        event = {
            'code': 802,
            'condition': 'current condition',
            'celsius': 28,
            'fahrenheit': 72,
        }

        profile = self.formatter._fill_profile(event, DisplayAddOrReplaceMessageProfile())
        self.assertTrue(isinstance(profile, DisplayAddOrReplaceMessageProfile), '_fill_profile should returns DisplayAddOrReplaceMessageProfile instance')
        self.assertEqual(profile.uuid, 'openweathermap', 'uuid field is invalid')
        self.assertTrue(len(profile.message)>0, 'Message field is invalid')

    def test_fill_profile_fahrenheit(self):
        event = {
            'code': 802,
            'condition': 'current condition',
            'fahrenheit': 72,
        }

        profile = self.formatter._fill_profile(event, DisplayAddOrReplaceMessageProfile())
        self.assertTrue(isinstance(profile, DisplayAddOrReplaceMessageProfile), '_fill_profile should returns DisplayAddOrReplaceMessageProfile instance')
        self.assertEqual(profile.uuid, 'openweathermap', 'uuid field is invalid')
        self.assertTrue(len(profile.message)>0, 'Message field is invalid')


if __name__ == "__main__":
    unittest.main()
    

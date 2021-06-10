import unittest
import logging
import os
import re
import sys
import json
import copy
sys.path.append('../')
from backend.openweathermap import Openweathermap
from cleep.exception import InvalidParameter, MissingParameter, CommandError, Unauthorized
from cleep.libs.tests import session
from backend.weathertonamedmessageformatter import WeatherToNamedMessageFormatter
from backend.openweathermapweatherupdateevent import OpenweathermapWeatherUpdateEvent
from cleep.profiles.namedmessageprofile import NamedMessageProfile
from mock import Mock, patch
import responses

class TestOpenweathermap(unittest.TestCase):

    FORECAST_SAMPLE = {
        "cod": "200",
        "message": 0,
        "cnt": 40,
        "list": [
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
    }
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
        logging.basicConfig(level=logging.FATAL, format=u'%(asctime)s %(name)s:%(lineno)d %(levelname)s : %(message)s')
        self.session = session.TestSession(self)

    def tearDown(self):
        self.session.clean()

    def init(self, start_module=True):
        self.module = self.session.setup(Openweathermap)
        if start_module:
            self.session.start_module(self.module)

    def test_configure(self):
        self.init(False)
        self.module._get_device_count = Mock(return_value=0)
        self.module._add_device = Mock()
        self.module.get_module_devices = Mock(return_value={
            '1234567890': {
                'type': 'dummy'
            }
        })

        self.session.start_module(self.module)

        self.module._add_device.assert_called_with({
            "type": "openweathermap",
            "name": "OpenWeatherMap",
            "lastupdate": None,
            "celsius": None,
            "fahrenheit": None,
            "humidity": None,
            "pressure": None,
            "windspeed": None,
            "winddirection": None,
            "code": None,
            "condition": None,
            "icon": None,
        })
        self.assertEqual(self.module._Openweathermap__owm_uuid, '1234567890')

    def test_configure_existing_device(self):
        self.init(False)
        self.module._get_device_count = Mock(return_value=1)
        self.module._add_device = Mock()
        self.module.get_module_devices = Mock(return_value={
            '1234567890': {
                'type': 'dummy'
            }
        })

        self.session.start_module(self.module)

        self.assertFalse(self.module._add_device.called)
        self.assertEqual(self.module._Openweathermap__owm_uuid, '1234567890')

    def test_on_start(self):
        self.init(False)
        self.module._force_weather_update = Mock()
        self.module._start_weather_task = Mock()

        self.session.start_module(self.module)

        self.module._force_weather_update.assert_called()
        self.module._start_weather_task.assert_called()

    def test_on_stop(self):
        self.init(False)
        self.module._stop_weather_task = Mock()

        self.session.start_module(self.module)
        self.module._on_stop()

        self.assertTrue(self.module._stop_weather_task.called)

    @patch('backend.openweathermap.Task')
    def test_start_weather_task(self, mock_task):
        self.init()

        self.module._start_weather_task()

        mock_task.assert_called()
        mock_task.return_value.start.assert_called()

    @patch('backend.openweathermap.Task')
    def test_start_weather_task_with_existing_task(self, mock_task):
        self.init()
        self.module.weather_task = 123

        self.module._start_weather_task()

        mock_task.return_value.start.assert_called()

    @patch('backend.openweathermap.Task')
    def test_stop_weather_task(self, mock_task):
        self.init()

        self.module._stop_weather_task()

        mock_task.return_value.stop.assert_called()

    @patch('backend.openweathermap.Task')
    def test_stop_weather_task_no_task(self, mock_task):
        self.init()
        self.module.weather_task = None

        self.module._stop_weather_task()

        self.assertFalse(mock_task.return_value.stop.called)

    def test_restart_weather_task(self):
        self.init()
        self.module._start_weather_task = Mock()
        self.module._stop_weather_task = Mock()

        self.module._restart_weather_task()

        self.module._start_weather_task.assert_called()
        self.module._stop_weather_task.assert_called()

    @responses.activate
    def test_owm_request(self):
        self.init()
        params = {'apikey': 'dummy'}
        responses.add(
            responses.GET,
            'http://url.com',
            body=json.dumps(params),
            status=200,
            match=[
                responses.urlencoded_params_matcher({"apikey": "dummy"})
            ]
        )

        resp = self.module._owm_request('http://url.com', params)
        logging.debug('Resp: %s' % str(resp))

        self.assertEqual(resp[0], 200)
        self.assertDictEqual(resp[1], params)

    @responses.activate
    def test_owm_request_failed(self):
        self.init()
        params = {'apikey': 'dummy'}
        responses.add(
            responses.GET,
            'http://url.com',
            body=json.dumps(params),
            status=404,
            match=[
                responses.urlencoded_params_matcher({"apikey": "dummy"})
            ]
        )

        resp = self.module._owm_request('http://url.com', params)
        logging.debug('Resp: %s' % str(resp))

        self.assertEqual(resp[0], 404)
        self.assertDictEqual(resp[1], params)

    @responses.activate
    def test_owm_request_exception(self):
        self.init()
        params = {'apikey': 'dummy'}
        responses.add(
            responses.GET,
            'http://url.com',
            body=Exception('Test exception'),
            status=404,
        )

        resp = self.module._owm_request('http://url.com', params)
        logging.debug('Resp: %s' % str(resp))

        self.assertIsNone(resp[0])
        self.assertIsNone(resp[1])

    def test__get_weather(self):
        self.init()
        position = {'latitude': 52.2040, 'longitude': 0.1208}
        self.session.add_mock_command(self.session.make_mock_command('get_position', position))
        self.module._owm_request = Mock(return_value=(200, self.WEATHER_SAMPLE))

        data = self.module._get_weather('apikey')
        logging.debug('Data: %s' % data)

        self.assertDictEqual(data, self.WEATHER_SAMPLE)

    def test__get_weather_invalid_params(self):
        self.init()

        with self.assertRaises(MissingParameter) as cm:
            self.module._get_weather(None)
        self.assertEqual(str(cm.exception), 'Parameter "apikey" is missing')

        with self.assertRaises(InvalidParameter) as cm:
            self.module._get_weather(True)
        self.assertEqual(str(cm.exception), 'Parameter "apikey" must be of type "str"')

    def test__get_weather_get_position_failed(self):
        self.init()
        position = {'latitude': 52.2040, 'longitude': 0.1208}
        self.session.add_mock_command(self.session.make_mock_command('get_position', position, fail=True))
        self.module._owm_request = Mock(return_value=(200, self.WEATHER_SAMPLE))

        with self.assertRaises(Exception) as cm:
            self.module._get_weather('apikey')
        self.assertTrue(str(cm.exception).startswith('Unable to get device position'))
        self.assertFalse(self.module._owm_request.called)

    def test__get_weather_owm_request_failed(self):
        self.init()
        position = {'latitude': 52.2040, 'longitude': 0.1208}
        self.session.add_mock_command(self.session.make_mock_command('get_position', position))

        self.module._owm_request = Mock(return_value=(401, None))
        with self.assertRaises(Exception) as cm:
            self.module._get_weather('apikey')
        self.assertEqual(str(cm.exception), 'Invalid OWM api key')
        
        self.module._owm_request = Mock(return_value=(203, self.WEATHER_SAMPLE))
        with self.assertRaises(Exception) as cm:
            self.module._get_weather('apikey')
        self.assertEqual(str(cm.exception), 'Error requesting openweathermap api (status 203)')

        weather_sample = copy.deepcopy(self.WEATHER_SAMPLE)
        del weather_sample['cod']
        self.module._owm_request = Mock(return_value=(200, weather_sample))
        with self.assertRaises(Exception) as cm:
            self.module._get_weather('apikey')
        self.assertEqual(str(cm.exception), 'Invalid OWM api response format. Is API changed?')

        weather_sample = copy.deepcopy(self.WEATHER_SAMPLE)
        weather_sample['cod'] = 400
        self.module._owm_request = Mock(return_value=(200, weather_sample))
        with self.assertRaises(Exception) as cm:
            self.module._get_weather('apikey')
        self.assertEqual(str(cm.exception), 'Unknown error from api')

    def test__get_weather_invalid_params(self):
        self.init()

        with self.assertRaises(MissingParameter) as cm:
            self.module._get_weather(None)
        self.assertEqual(str(cm.exception), 'Parameter "apikey" is missing')

        with self.assertRaises(InvalidParameter) as cm:
            self.module._get_weather(True)
        self.assertEqual(str(cm.exception), 'Parameter "apikey" must be of type "str"')

    def test__get_forecast(self):
        self.init()
        position = {'latitude': 52.2040, 'longitude': 0.1208}
        self.session.add_mock_command(self.session.make_mock_command('get_position', position))
        self.module._owm_request = Mock(return_value=(200, self.FORECAST_SAMPLE))

        data = self.module._get_forecast('apikey')
        logging.debug('Data: %s' % data)

        self.assertListEqual(data, self.FORECAST_SAMPLE['list'])

    def test__get_forecast_invalid_params(self):
        self.init()

        with self.assertRaises(MissingParameter) as cm:
            self.module._get_forecast(None)
        self.assertEqual(str(cm.exception), 'Parameter "apikey" is missing')

        with self.assertRaises(InvalidParameter) as cm:
            self.module._get_forecast(True)
        self.assertEqual(str(cm.exception), 'Parameter "apikey" must be of type "str"')

    def test__get_forecast_get_position_failed(self):
        self.init()
        position = {'latitude': 52.2040, 'longitude': 0.1208}
        self.session.add_mock_command(self.session.make_mock_command('get_position', position, fail=True))
        self.module._owm_request = Mock(return_value=(200, self.FORECAST_SAMPLE))

        with self.assertRaises(Exception) as cm:
            self.module._get_forecast('apikey')
        self.assertTrue(str(cm.exception).startswith('Unable to get device position'))
        self.assertFalse(self.module._owm_request.called)

    def test__get_forecast_owm_request_failed(self):
        self.init()
        position = {'latitude': 52.2040, 'longitude': 0.1208}
        self.session.add_mock_command(self.session.make_mock_command('get_position', position))

        self.module._owm_request = Mock(return_value=(401, None))
        with self.assertRaises(Exception) as cm:
            self.module._get_forecast('apikey')
        self.assertEqual(str(cm.exception), 'Invalid OWM api key')
        
        self.module._owm_request = Mock(return_value=(203, self.FORECAST_SAMPLE))
        with self.assertRaises(Exception) as cm:
            self.module._get_forecast('apikey')
        self.assertEqual(str(cm.exception), 'Error requesting openweathermap api (status 203)')

        forecast_sample = copy.deepcopy(self.FORECAST_SAMPLE)
        del forecast_sample['cod']
        self.module._owm_request = Mock(return_value=(200, forecast_sample))
        with self.assertRaises(Exception) as cm:
            self.module._get_forecast('apikey')
        self.assertEqual(str(cm.exception), 'Invalid OWM api response format. Is API changed?')

        forecast_sample = copy.deepcopy(self.FORECAST_SAMPLE)
        forecast_sample['cod'] = 400
        self.module._owm_request = Mock(return_value=(200, forecast_sample))
        with self.assertRaises(Exception) as cm:
            self.module._get_forecast('apikey')
        self.assertEqual(str(cm.exception), 'API message: 0')

        forecast_sample = copy.deepcopy(self.FORECAST_SAMPLE)
        forecast_sample['list'] = []
        self.module._owm_request = Mock(return_value=(200, forecast_sample))
        with self.assertRaises(Exception) as cm:
            self.module._get_forecast('apikey')
        self.assertEqual(str(cm.exception), 'No forecast data retrieved')

    def test_weather_task(self):
        self.init(False)
        self.module._get_config = Mock(return_value={'apikey': 'apikey', 'devices': {'1234567890': {}}})
        self.module._get_weather = Mock(return_value=self.WEATHER_SAMPLE)
        self.module._get_forecast = Mock(return_value=self.FORECAST_SAMPLE['list'])
        self.module._get_devices = Mock(return_value={'1234567890': {}})
        self.session.start_module(self.module)
        self.module._Openweathermap__owm_uuid = '1234567890'

        self.module._weather_task()
        logging.debug('Event params: %s' % self.session.get_last_event_params('openweathermap.weather.update'))

        self.session.assert_event_called_with(
            'openweathermap.weather.update',
            {
                'lastupdate': session.AnyArg(),
                'icon': 'https://openweathermap.org/img/wn/01n.png',
                'condition': 'Clear sky',
                'code': 800,
                'celsius': 11.23,
                'fahrenheit': 52.214,
                'pressure': 1023,
                'humidity': 71,
                'windspeed': 3.1,
                'winddirection': 'NE',
                'winddegrees': 20,
            }
        )

    def test_weather_task_no_apikey(self):
        self.init(False)
        self.module._get_config = Mock(return_value={'apikey': None, 'devices': {'1234567890': {}}})
        self.module._get_weather = Mock(return_value=self.WEATHER_SAMPLE)
        self.module._get_forecast = Mock(return_value=self.FORECAST_SAMPLE['list'])
        self.session.start_module(self.module)
        self.module._Openweathermap__owm_uuid = '1234567890'

        self.module._weather_task()
        
        self.assertFalse(self.module._get_weather.called)
        self.assertFalse(self.module._get_forecast.called)

    def test_weather_task_no_weather(self):
        self.init(False)
        self.module._get_config = Mock(return_value={'apikey': 'apikey', 'devices': {'1234567890': {}}})
        weather_sample = copy.deepcopy(self.WEATHER_SAMPLE)
        del weather_sample['weather']
        self.module._get_weather = Mock(return_value=weather_sample)
        self.module._get_forecast = Mock(return_value=self.FORECAST_SAMPLE['list'])
        self.module._get_devices = Mock(return_value={'1234567890': {}})
        self.session.start_module(self.module)
        self.module._Openweathermap__owm_uuid = '1234567890'

        self.module._weather_task()
        logging.debug('Event params: %s' % self.session.get_last_event_params('openweathermap.weather.update'))

        self.session.assert_event_called_with(
            'openweathermap.weather.update',
            {
                'lastupdate': session.AnyArg(),
                'icon': 'https://openweathermap.org/img/wn/unknown.png',
                'condition': '?',
                'code': 0,
                'celsius': 11.23,
                'fahrenheit': 52.214,
                'pressure': 1023,
                'humidity': 71,
                'windspeed': 3.1,
                'winddirection': 'NE',
                'winddegrees': 20,
            }
        )

    def test_weather_task_no_main(self):
        self.init(False)
        self.module._get_config = Mock(return_value={'apikey': 'apikey', 'devices': {'1234567890': {}}})
        weather_sample = copy.deepcopy(self.WEATHER_SAMPLE)
        del weather_sample['main']
        self.module._get_weather = Mock(return_value=weather_sample)
        self.module._get_forecast = Mock(return_value=self.FORECAST_SAMPLE['list'])
        self.module._get_devices = Mock(return_value={'1234567890': {}})
        self.session.start_module(self.module)
        self.module._Openweathermap__owm_uuid = '1234567890'

        self.module._weather_task()
        logging.debug('Event params: %s' % self.session.get_last_event_params('openweathermap.weather.update'))

        self.session.assert_event_called_with(
            'openweathermap.weather.update',
            {
                'lastupdate': session.AnyArg(),
                'icon': 'https://openweathermap.org/img/wn/01n.png',
                'condition': 'Clear sky',
                'code': 800,
                'celsius': 0.0,
                'fahrenheit': 0.0,
                'pressure': 0.0,
                'humidity': 0.0,
                'windspeed': 3.1,
                'winddirection': 'NE',
                'winddegrees': 20,
            }
        )

    def test_weather_task_no_wind(self):
        self.init(False)
        self.module._get_config = Mock(return_value={'apikey': 'apikey', 'devices': {'1234567890': {}}})
        weather_sample = copy.deepcopy(self.WEATHER_SAMPLE)
        del weather_sample['wind']
        self.module._get_weather = Mock(return_value=weather_sample)
        self.module._get_forecast = Mock(return_value=self.FORECAST_SAMPLE['list'])
        self.module._get_devices = Mock(return_value={'1234567890': {}})
        self.session.start_module(self.module)
        self.module._Openweathermap__owm_uuid = '1234567890'

        self.module._weather_task()
        logging.debug('Event params: %s' % self.session.get_last_event_params('openweathermap.weather.update'))

        self.session.assert_event_called_with(
            'openweathermap.weather.update',
            {
                'lastupdate': session.AnyArg(),
                'icon': 'https://openweathermap.org/img/wn/01n.png',
                'condition': 'Clear sky',
                'code': 800,
                'celsius': 11.23,
                'fahrenheit': 52.214,
                'pressure': 1023,
                'humidity': 71.0,
                'windspeed': 0.0,
                'winddirection': 'N',
                'winddegrees': 0,
            }
        )

    def test_weather_task_exception(self):
        self.init()
        self.module._get_config = Mock(side_effect=Exception('Test exception'))
        self.module._get_weather = Mock(return_value=self.WEATHER_SAMPLE)
        self.module._get_forecast = Mock(return_value=self.FORECAST_SAMPLE['list'])

        self.module._weather_task()

        self.assertFalse(self.module._get_weather.called)
        self.assertFalse(self.module._get_forecast.called)

    def test_set_apikey_valid(self):
        self.init()
        position = {'latitude': 52.2040, 'longitude': 0.1208}
        self.session.add_mock_command(self.session.make_mock_command('get_position', position))
        self.module._get_weather = Mock()
        self.module._restart_weather_task = Mock()
        self.module._force_weather_update = Mock()
        self.module._update_config = Mock()

        self.module.set_apikey('apikey')

        self.module._get_weather.assert_called()
        self.module._restart_weather_task.assert_called()
        self.module._force_weather_update.assert_called()
        self.module._update_config.assert_called_with({'apikey': 'apikey'})

    def test_set_apikey_check_parameters(self):
        self.init()
        position = {'latitude': 52.2040, 'longitude': 0.1208}
        self.session.add_mock_command(self.session.make_mock_command('get_position', position))
        self.module._get_weather = Mock()

        with self.assertRaises(InvalidParameter) as cm:
            self.module.set_apikey('')
        self.assertEqual(str(cm.exception), 'Parameter "apikey" is invalid (specified="")')

        with self.assertRaises(MissingParameter) as cm:
            self.module.set_apikey(None)
        self.assertEqual(str(cm.exception), 'Parameter "apikey" is missing')

    def test_get_weather(self):
        self.init()
        self.module._Openweathermap__owm_uuid = '1234567890'
        self.module._get_devices = Mock(return_value={'1234567890': {'weather': 'data'}})

        data = self.module.get_weather()

        self.assertDictEqual(data, {'weather': 'data'})

    def test_get_forecast(self):
        self.init()
        self.module._Openweathermap__forecast = 'forecast'

        data = self.module.get_forecast()

        self.assertEqual(data, 'forecast')
    

class TestWeatherToNamedMessageFormatter(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.FATAL, format=u'%(asctime)s %(name)s:%(lineno)d %(levelname)s : %(message)s')
        self.session = session.TestSession(self)

        self.formatter = WeatherToNamedMessageFormatter({'events_broker': Mock()})

    def tearDown(self):
        self.session.clean()

    def test_fill_profile(self):
        event = {
            'code': 802,
            'condition': 'current condition',
            'celsius': 28,
            'fahrenheit': 72,
        }

        profile = self.formatter._fill_profile(event, NamedMessageProfile())
        self.assertTrue(isinstance(profile, NamedMessageProfile), '_fill_profile should returns NamedMessageProfile instance')
        self.assertEqual(profile.name, 'openweathermap', 'name field is invalid')
        self.assertTrue(len(profile.message)>0, 'Message field is invalid')

    def test_fill_profile_fahrenheit(self):
        event = {
            'code': 802,
            'condition': 'current condition',
            'fahrenheit': 72,
        }

        profile = self.formatter._fill_profile(event, NamedMessageProfile())
        self.assertTrue(isinstance(profile, NamedMessageProfile), '_fill_profile should returns NamedMessageProfile instance')
        self.assertEqual(profile.name, 'openweathermap', 'name field is invalid')
        self.assertTrue(len(profile.message)>0, 'Message field is invalid')




class TestsOpenweathermapWeatherUpdateEvent(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.FATAL, format=u'%(asctime)s %(name)s:%(lineno)d %(levelname)s : %(message)s')
        self.session = session.TestSession(self)
        self.event = self.session.setup_event(OpenweathermapWeatherUpdateEvent)

    def test_event_params(self):
        self.assertListEqual(self.event.EVENT_PARAMS, [
            "icon",
            "condition",
            "code",
            "celsius",
            "fahrenheit",
            "pressure",
            "humidity",
            "windspeed",
            "winddegrees",
            "winddirection",
            "lastupdate",
        ])



if __name__ == "__main__":
    # coverage run --omit="*/lib/python*/*","test_*" --concurrency=thread test_teleinfo.py; coverage report -m -i
    unittest.main()


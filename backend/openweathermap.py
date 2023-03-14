#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import requests
from cleep.libs.internals.task import Task
from cleep.core import CleepModule
from cleep.common import CATEGORIES

__all__ = ["Openweathermap"]


class Openweathermap(CleepModule):
    """
    OpenWeatherMap application.
    Returns current weather conditions and forecast.

    Note:
        https://openweathermap.org/api
    """

    MODULE_AUTHOR = "Cleep"
    MODULE_VERSION = "1.2.4"
    MODULE_DEPS = []
    MODULE_CATEGORY = CATEGORIES.SERVICE
    MODULE_DESCRIPTION = "Gets weather conditions using OpenWeatherMap service"
    MODULE_LONGDESCRIPTION = (
        "This application gets data from OpenWeatherMap online service and displays it directly on your device "
        "dashboard.<br>OpenWeatherMap allows to get for free current weather condition and 5 days forecast.<br> "
        "This application also broadcasts weather event on all your devices."
    )
    MODULE_TAGS = ["weather", "forecast"]
    MODULE_URLINFO = "https://github.com/CleepDevice/cleepapp-openweathermap"
    MODULE_URLHELP = None
    MODULE_URLSITE = "https://openweathermap.org/"
    MODULE_URLBUGS = "https://github.com/CleepDevice/cleepapp-openweathermap/issues"

    MODULE_CONFIG_FILE = "openweathermap.conf"
    DEFAULT_CONFIG = {"apikey": None}

    OWM_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
    OWM_FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
    OWM_ICON_URL = "https://openweathermap.org/img/wn/{0}.png"
    OWM_TASK_DELAY = 900
    OWM_PREVENT_FLOOD = 15
    OWM_WEATHER_CODES = {
        200: "Thunderstorm with light rain",
        201: "Thunderstorm with rain",
        202: "Thunderstorm with heavy rain",
        210: "Light thunderstorm",
        211: "Thunderstorm",
        212: "Heavy thunderstorm",
        221: "Ragged thunderstorm",
        230: "Thunderstorm with light drizzle",
        231: "Thunderstorm with drizzle",
        232: "Thunderstorm with heavy drizzle",
        300: "Light intensity drizzle",
        301: "Drizzle",
        302: "Heavy intensity drizzle",
        310: "Light intensity drizzle rain",
        311: "Drizzle rain",
        312: "Heavy intensity drizzle rain",
        313: "Shower rain and drizzle",
        314: "Heavy shower rain and drizzle",
        321: "Shower drizzle",
        500: "Light rain",
        501: "Moderate rain",
        502: "Heavy intensity rain",
        503: "Very heavy rain",
        504: "Extreme rain",
        511: "Freezing rain",
        520: "Light intensity shower rain",
        521: "Shower rain",
        522: "Heavy intensity shower rain",
        531: "Ragged shower rain",
        600: "Light snow",
        601: "Snow",
        602: "Heavy snow",
        611: "Sleet",
        612: "Shower sleet",
        615: "Light rain and snow",
        616: "Rain and snow",
        620: "Light shower snow",
        621: "Shower snow",
        622: "Heavy shower snow",
        701: "Mist",
        711: "Smoke",
        721: "Haze",
        731: "Sand, dust whirls",
        741: "Fog",
        751: "Sand",
        761: "Dust",
        762: "Volcanic ash",
        771: "Squalls",
        781: "Tornado",
        800: "Clear sky",
        801: "Few clouds",
        802: "Scattered clouds",
        803: "Broken clouds",
        804: "Overcast clouds",
        900: "Tornado",
        901: "Tropical storm",
        902: "Hurricane",
        903: "Cold",
        904: "Hot",
        905: "Windy",
        906: "Hail",
        951: "Calm",
        952: "Light breeze",
        953: "Gentle breeze",
        954: "Moderate breeze",
        955: "Fresh breeze",
        956: "Strong breeze",
        957: "High wind, near gale",
        958: "Gale",
        959: "Severe gale",
        960: "Storm",
        961: "Violent storm",
        962: "Hurricane",
    }
    OWM_WIND_DIRECTIONS = [
        "N",
        "NNE",
        "NE",
        "ENE",
        "E",
        "ESE",
        "SE",
        "SSE",
        "S",
        "SSW",
        "SW",
        "WSW",
        "W",
        "WNW",
        "NW",
        "NNW",
        "N",
    ]

    def __init__(self, bootstrap, debug_enabled):
        """
        Constructor

        Args:
            bootstrap (dict): bootstrap objects
            debug_enabled (bool): flag to set debug level to logger
        """
        # init
        CleepModule.__init__(self, bootstrap, debug_enabled)

        # members
        self.weather_task = None
        self.__owm_uuid = None
        self.__forecast = []

        # events
        self.openweathermap_weather_update = self._get_event(
            "openweathermap.weather.update"
        )

    def _configure(self):
        """
        Configure module
        """
        # add openweathermap device
        if self._get_device_count() == 0:
            owm = {
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
            }
            self._add_device(owm)

        # get device uuid
        devices = self.get_module_devices()
        self.__owm_uuid = list(devices.keys())[0]

    def _on_start(self):
        """
        Module starts
        """
        # update weather conditions
        self._force_weather_update()

        # start weather task
        self._start_weather_task()

    def _on_stop(self):
        """
        Module stops
        """
        self._stop_weather_task()

    def _force_weather_update(self):
        """
        Force weather update according to last update to not flood owm api
        """
        # get devices if not provided
        devices = self.get_module_devices()

        last_update = devices[self.__owm_uuid].get("lastupdate")
        if last_update is None or last_update + self.OWM_PREVENT_FLOOD < time.time():
            self._weather_task()

    def _start_weather_task(self):
        """
        Start weather task
        """
        if self.weather_task is None:
            self.weather_task = Task(
                self.OWM_TASK_DELAY, self._weather_task, self.logger
            )
            self.weather_task.start()

    def _stop_weather_task(self):
        """
        Stop weather task
        """
        if self.weather_task is not None:
            self.weather_task.stop()

    def _restart_weather_task(self):
        """
        Restart weather task
        """
        self._stop_weather_task()
        self._start_weather_task()

    def _owm_request(self, url, params):
        """
        Request OWM api

        Args:
            url (string): request url
            params (dict): dict of parameters

        Returns:
            tuple: request response::

                (
                    status (int): request status code,
                    data (dict): request response data
                )

        """
        status = None
        resp_data = None
        try:
            self.logger.debug("Request params: %s", params)
            resp = requests.get(url, params=params)
            resp_data = resp.json()
            self.logger.debug("Response data: %s", resp_data)
            status = resp.status_code
            if status != 200:
                self.logger.error("OWM api response [%s]: %s", status, resp_data)

        except Exception:
            self.logger.exception("Error while requesting OWM API:")

        return (status, resp_data)

    def _get_weather(self, apikey):
        """
        Get weather condition

        Args:
            apikey (string): OWM apikey

        Returns:
            dict: weather conditions (see http://openweathermap.org/current#parameter for output format)

        Raises:
            InvalidParameter: if input parameter is invalid
            CommandError: if command failed
        """
        # check parameter
        self._check_parameters([{"name": "apikey", "value": apikey, "type": str}])

        # get position infos from parameters app
        resp = self.send_command("get_position", "parameters")
        self.logger.debug("Get position from parameters module resp: %s", resp)
        if not resp or resp.error:
            message = resp.error if resp else "No response"
            raise Exception(f"Unable to get device position ({message})")
        position = resp.data

        # request api
        (status, resp) = self._owm_request(
            self.OWM_WEATHER_URL,
            {
                "appid": apikey,
                "lat": position["latitude"],
                "lon": position["longitude"],
                "units": "metric",
                "mode": "json",
            },
        )
        self.logger.debug("OWM response: %s", resp)

        # handle errors
        if status == 401:
            raise Exception("Invalid OWM api key")
        if status != 200:
            raise Exception(f"Error requesting openweathermap api (status {status})")
        if not isinstance(resp, dict) or "cod" not in resp:
            raise Exception("Invalid OWM api response format. Is API changed?")
        if resp["cod"] != 200:  # cod is int for weather request
            raise Exception(
                resp["message"] if "message" in resp else "Unknown error from api"
            )

        return resp

    def _get_forecast(self, apikey):
        """
        Get forecast (5 days with 3 hours step)

        Args:
            apikey (string): OWM apikey

        Returns:
            dict: forecast (see http://openweathermap.org/forecast5 for output format)

        Raises:
            InvalidParameter: if input parameter is invalid
            CommandError: if command failed
        """
        # check parameter
        self._check_parameters([{"name": "apikey", "value": apikey, "type": str}])

        # get position infos from parameters app
        resp = self.send_command("get_position", "parameters")
        self.logger.debug("Get position from parameters module resp: %s", resp)
        if not resp or resp.error:
            message = resp.error if resp else "No response"
            raise Exception(f"Unable to get device position ({message})")
        position = resp.data

        # request api
        (status, resp) = self._owm_request(
            self.OWM_FORECAST_URL,
            {
                "appid": apikey,
                "lat": position["latitude"],
                "lon": position["longitude"],
                "units": "metric",
                "mode": "json",
            },
        )
        self.logger.trace("OWM response: %s", resp)

        # handle errors
        if status == 401:
            raise Exception("Invalid OWM api key")
        if status != 200:
            raise Exception(f"Error requesting openweathermap api (status {status})")
        if "cod" not in resp:
            raise Exception("Invalid OWM api response format. Is API changed?")
        if resp["cod"] != "200":  # cod is string for forecast request
            message = resp["message"] if "message" in resp else "Unknown error from api"
            raise Exception(f"API message: {message}")
        if "list" not in resp or len(resp["list"]) == 0:
            raise Exception("No forecast data retrieved")

        return resp["list"]

    def _weather_task(self):
        """
        Weather task in charge to refresh weather condition every hours
        Send openweathermap.weather.update event with following data::

            {
                lastupdate (int): timestamp,
                icon (string): openweathermap icon,
                condition (string): openweathermap condition string (english),
                code (int): openweather condition code,
                celsius (float): current temperature in celsius,
                fahrenheit (float): current temperature in fahrenheit,
                pressure (float): current pressure,
                humidity (float): current humidity,
                windspeed (float): current wind speed,
                winddirection (string): current wind direction,
                winddegrees (float): current wind degrees
            }

        """
        try:
            self.logger.debug("Update weather conditions")

            # get api key
            config = self._get_config()
            if config["apikey"] is None or len(config["apikey"]) == 0:
                self.logger.debug("No apikey configured")
                return

            # apikey configured, get weather
            weather = self._get_weather(config["apikey"])
            self.logger.debug("Weather: %s", weather)
            self.__forecast = self._get_forecast(config["apikey"])
            self.logger.debug("Forecast: %s", self.__forecast)

            # save current weather conditions
            device = self._get_devices()[self.__owm_uuid]
            device["lastupdate"] = int(time.time())
            if "weather" in weather and len(weather["weather"]) > 0:
                icon = weather["weather"][0].get("icon")
                device["icon"] = self.OWM_ICON_URL.format(icon or "unknown")
                wid = weather["weather"][0].get("id")
                device["condition"] = self.OWM_WEATHER_CODES[wid] if wid else "?"
                device["code"] = int(wid) if wid else 0
            else:
                device["icon"] = self.OWM_ICON_URL.format("unknown")
                device["condition"] = "?"
                device["code"] = 0
            if "main" in weather:
                device["celsius"] = weather["main"].get("temp", 0.0)
                device["fahrenheit"] = (
                    weather["main"].get("temp", 0.0) * 9.0 / 5.0 + 32.0
                )
                device["pressure"] = weather["main"].get("pressure", 0.0)
                device["humidity"] = weather["main"].get("humidity", 0.0)
            else:
                device["celsius"] = 0.0
                device["fahrenheit"] = 0.0
                device["pressure"] = 0.0
                device["humidity"] = 0.0
            if "wind" in weather:
                device["windspeed"] = weather["wind"].get("speed", 0.0)
                device["winddegrees"] = weather["wind"].get("deg", 0)
                index = int(round((weather["wind"].get("deg", 0) % 360) / 22.5) + 1)
                device["winddirection"] = self.OWM_WIND_DIRECTIONS[
                    0 if index >= 17 else index
                ]
            else:
                device["windspeed"] = 0.0
                device["winddegrees"] = 0.0
                device["winddirection"] = "N"

            self._update_device(self.__owm_uuid, device)

            # and emit event
            event_keys = [
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
            ]
            self.openweathermap_weather_update.send(
                params={k: v for k, v in device.items() if k in event_keys},
                device_id=self.__owm_uuid,
            )

        except Exception:
            self.logger.exception("Exception during weather task:")

    def set_apikey(self, apikey):
        """
        Set openweathermap apikey

        Args:
            apikey (string): OWM apikey

        Returns:
            bool: True if apikey saved successfully

        Raises:
            CommandError: if error occured while using apikey to get current weather
        """
        self._check_parameters([{"name": "apikey", "value": apikey, "type": str}])

        # test apikey (should raise exception if error)
        self._get_weather(apikey)

        # test succeed, update weather right now and restart task
        self._restart_weather_task()
        self._force_weather_update()

        # save config
        return self._update_config({"apikey": apikey})

    def get_weather(self):
        """
        Return current weather conditions
        Useful to use it in action script

        Returns:
            dict: device information
        """
        return self._get_devices()[self.__owm_uuid]

    def get_forecast(self):
        """
        Return last forecast information.
        May be empty if cleep just restarted.

        Returns:
            list: list of forecast data (every 3 hours)
        """
        return self.__forecast

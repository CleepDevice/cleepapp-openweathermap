#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cleep.libs.internals.event import Event

class OpenweathermapWeatherUpdateEvent(Event):
    """
    Openweathermap.weather.update event
    """

    EVENT_NAME = "openweathermap.weather.update"
    EVENT_PROPAGATE = True
    EVENT_PARAMS = [
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

    def __init__(self, params):
        """
        Constructor

        Args:
            params (dict): event parameters
        """
        Event.__init__(self, params)

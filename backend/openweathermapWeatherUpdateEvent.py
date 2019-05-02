#!/usr/bin/env python
# -*- coding: utf-8 -*-

from raspiot.events.event import Event

class OpenweathermapWeatherUpdateEvent(Event):
    """
    Openweathermap.weather.update event
    """

    EVENT_NAME = u'openweathermap.weather.update'
    EVENT_SYSTEM = False

    def __init__(self, bus, formatters_factory, events_factory):
        """ 
        Constructor

        Args:
            bus (MessageBus): message bus instance
            formatters_factory (FormattersFactory): formatters factory instance
            events_factory (EventsFactory): events factory instance
        """
        Event.__init__(self, bus, formatters_factory, events_factory)

    def _check_params(self, params):
        """
        Check event parameters

        Args:
            params (dict): event parameters

        Return:
            bool: True if params are valid, False otherwise
        """
        keys = [
            u'icon',
            u'condition',
            u'code',
            u'celsius',
            u'fahrenheit',
            u'pressure',
            u'humidity',
            u'windspeed',
            u'winddegrees',
            u'winddirection',
            u'lastupdate',
        ]
        return all(key in keys for key in params.keys())

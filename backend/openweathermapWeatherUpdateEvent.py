#!/usr/bin/env python
# -*- coding: utf-8 -*-

from raspiot.libs.internals.event import Event

class OpenweathermapWeatherUpdateEvent(Event):
    """
    Openweathermap.weather.update event
    """

    EVENT_NAME = u'openweathermap.weather.update'
    EVENT_SYSTEM = False
    EVENT_PARAMS = [u'icon', u'condition', u'code', u'celsius', u'fahrenheit', u'pressure', u'humidity', u'windspeed', u'winddegrees', u'winddirection', u'lastupdate']

    def __init__(self, bus, formatters_broker, events_broker):
        """ 
        Constructor

        Args:
            bus (MessageBus): message bus instance
            formatters_broker (FormattersBroker): formatters broker instance
            events_broker (EventsBroker): events broker instance
        """
        Event.__init__(self, bus, formatters_broker, events_broker)


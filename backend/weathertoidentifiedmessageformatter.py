#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cleep.libs.internals.profileformatter import ProfileFormatter
from cleep.profiles.identifiedmessageprofile import IdentifiedMessageProfile


class WeatherToIdentifiedMessageFormatter(ProfileFormatter):
    """
    Openweathermap data to IdentifiedMessageProfile
    """

    CODES = {
        200: ":stormy:",
        201: ":stormy:",
        202: ":stormy:",
        210: ":stormy:",
        211: ":stormy:",
        212: ":stormy:",
        221: ":stormy:",
        230: ":stormy:",
        231: ":stormy:",
        232: ":stormy:",
        300: ":rainy:",
        301: ":rainy:",
        302: ":rainy:",
        310: ":rainy:",
        311: ":rainy:",
        312: ":rainy:",
        313: ":rainy:",
        314: ":rainy:",
        321: ":rainy:",
        500: ":rainy:",
        501: ":rainy:",
        502: ":rainy:",
        503: ":rainy:",
        504: ":rainy:",
        511: ":rainy:",
        520: ":rainy:",
        521: ":rainy:",
        522: ":rainy:",
        531: ":rainy:",
        600: ":snowy:",
        601: ":snowy:",
        602: ":snowy:",
        611: ":snowy:",
        612: ":snowy:",
        615: ":rainy:",
        616: ":rainy:",
        620: ":rainy:",
        621: ":rainy:",
        622: ":rainy:",
        701: ":rainy:",
        711: ":fogggy:",
        721: ":foggy:",
        731: ":cloudy:",
        741: ":foggy:",
        751: ":cloudy:",
        761: ":cloudy:",
        762: ":foggy:",
        771: ":stormy:",
        781: ":stormy:",
        800: ":sunny:",
        801: ":cloudy:",
        802: ":cloudy:",
        803: ":cloudy:",
        804: ":cloudy:",
        900: ":stormy:",
        901: ":stormy:",
        902: ":stormy:",
        903: ":snowy:",
        904: ":sunny:",
        905: ":stormy:",
        906: ":foggy:",
        951: ":sunny:",
        952: ":cloudy:",
        953: ":cloudy:",
        954: ":cloudy:",
        955: ":cloudy:",
        956: ":cloudy:",
        957: ":cloudy:",
        958: ":cloudy:",
        959: ":cloudy:",
        960: ":stormy:",
        961: ":stormy:",
        962: ":cloudy:",
    }

    def __init__(self, params):
        """
        Constructor

        Args:
            params (dict): formatter parameters
        """
        ProfileFormatter.__init__(
            self, params, "openweathermap.weather.update", IdentifiedMessageProfile()
        )

    def _fill_profile(self, event_params, profile):
        """
        Fill profile with event data

        Args:
            event_params (dict): event parameters
            profile (Profile): profile instance
        """
        profile.id = "openweathermap"
        profile.message = ""

        # append icon
        if "code" in event_params and event_params["code"] in self.CODES:
            profile.message += f"{self.CODES[event_params['code']]} "

        # append current weather conditions
        if "condition" in event_params:
            profile.message += event_params["condition"]

        # append current temperature
        temp = "?"
        unit = "C"
        if "celsius" in event_params:
            temp = event_params["celsius"]
            unit = "C"
        elif "fahrenheit" in event_params:
            temp = event_params["fahrenheit"]
            unit = "F"
        profile.message += f" {temp}\N{DEGREE SIGN}{unit}"

        return profile

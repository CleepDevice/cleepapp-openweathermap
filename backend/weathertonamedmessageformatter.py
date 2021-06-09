#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cleep.libs.internals.profileformatter import ProfileFormatter
from cleep.profiles.namedmessageprofile import NamedMessageProfile


class WeatherToNamedMessageFormatter(ProfileFormatter):
    """
    Openweathermap data to NamedMessageProfile
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
            self, params, "openweathermap.weather.update", NamedMessageProfile()
        )

    def _fill_profile(self, event_values, profile):
        """
        Fill profile with event data

        Args:
            event_values (dict): event values
            profile (Profile): profile instance
        """
        profile.name = "openweathermap"
        profile.message = ""

        # append icon
        if event_values.has_key("code") and event_values["code"] in self.CODES.keys():
            profile.message += "%s " % self.CODES[event_values["code"]]

        # append current weather conditions
        if event_values.has_key("condition"):
            profile.message += event_values["condition"]

        # append current temperature
        if event_values.has_key("celsius"):
            profile.message += " %s%sC" % (event_values["celsius"], "\N{DEGREE SIGN}")
        elif event_values.has_key("fahrenheit"):
            profile.message += " %s%sF" % (
                event_values["fahrenheit"],
                "\N{DEGREE SIGN}",
            )

        return profile

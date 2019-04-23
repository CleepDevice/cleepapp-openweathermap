import unittest
import logging
import sys
sys.path.append('../')
from backend.openweathermap import Openweathermap
from raspiot.utils import InvalidParameter, MissingParameter, CommandError, Unauthorized
from raspiot.libs.tests import session

LOG_LEVEL = logging.INFO

class TestOpenweathermap(unittest.TestCase):

    def setUp(self):
        self.session = session.Session(LOG_LEVEL)
        self.module = self.session.setup(Openweathermap)

    def tearDown(self):
        self.session.clean()

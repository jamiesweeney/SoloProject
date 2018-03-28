import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app
import unittest
import tempfile

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        app.app.config["TESTING"] = True

    def tearDown(self):
        app.app.config["TESTING"] = False


    #-- Test that app is in testing mode --#
    def testTestingTrue(self):
        assert app.app.config["TESTING"]


    #-- Test public web pages --#
    def testBaseURL(self):
        print ((app.wp_home()))


    #
    # def testHomeURL(self):
    #
    #
    # def testBuildingURL(self):
    #
    #
    # def testFloorURL(self):
    #
    #
    # def testRoomURL(self):
    #
    #
    # def testLogin(self):
    #
    #
    # #-- Test admin web pages --#
    #
    # def testAdmin(self):
    #
    # def testLogout(self):
    #
    #
    # #-- Test public GET requests --#
    #
    #
    # #-- Test admin GET requests --#
    #
    #
    # #-- Test admin POST requests --#
    #
    #
    # #-- Test RPi POST requests --#
    #
    #
    # #-- Test URL management --#
    #


if __name__ == '__main__':
    unittest.main()

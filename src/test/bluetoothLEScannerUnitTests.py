
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Test address hashing

from sensors import bluetoothLEScanner as btle
import unittest

class TestAddressHashing(unittest.TestCase):

    def test_null(self):
        address = None
        self.assertTrue(btle.hash_address(address) == None)

        address = ""
        self.assertTrue(btle.hash_address(address) == None)

    def test_valid(self):
        address = "30:10:B3:21:2D:3E"
        ans1 = btle.hash_address(address)
        self.assertTrue(ans1 != None)
        self.assertTrue(ans1 != address)
        self.assertTrue(len(ans1) == 28)
        self.assertTrue(ans1 == btle.hash_address(address))

        address = "3010B3212D3E"
        ans2 = btle.hash_address(address)
        self.assertTrue(ans2 != None)
        self.assertTrue(ans2 != address)
        self.assertTrue(len(ans2) == 28)
        self.assertTrue(ans2 == btle.hash_address(address))

        self.assertTrue(ans1 == ans2)



class TestDeviceLogging(unittest.TestCase):

    def setUp(self):
        config.BLUETOOTHLE_SCANNER_LOG == "test"

    def test_null(self):
        print (config.BLUETOOTHLE_SCANNER_LOG)
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()

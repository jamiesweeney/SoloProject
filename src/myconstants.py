import os

#Directories
BASE_DIR = os.path.dirname(os.path.realpath(__file__))

LOG_DIR = os.path.join(BASE_DIR + "/logs")

SCANNERS_DIR = os.path.join(BASE_DIR + "/scanners")
SENSORS_DIR = os.path.join(BASE_DIR + "/sensors")


#Log files
BT_LOG = os.path.join(LOG_DIR + "/bluetoothScanner.log")
BTLE_LOG = os.path.join(LOG_DIR + "/bluetoothLEScanner.log")

#Startup scripts
BT_SETUP_SCRIPT = os.path.join(SCANNERS_DIR + "/setupBluetooth.sh")

#Scanners
BT_SCANNER = os.path.join(SCANNERS_DIR + "/bluetoothScanner.py")
BTLE_SCANNER = os.path.join(SCANNERS_DIR + "/bluetoothLEScanner.py")

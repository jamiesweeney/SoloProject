import os 



#Directories
BASE_DIR = os.path.dirname(os.path.realpath(__file__))

LOG_DIR = os.path.join(BASE_DIR + "/Logs")

SCANNERS_DIR = os.path.join(BASE_DIR + "/Scanners")
SENSORS_DIR = os.path.join(BASE_DIR + "/Sensors")


#Log files
BT_LOG = os.path.join(LOG_DIR + "/bluetoothScanner.log")
BTLE_LOG = os.path.join(LOG_DIR + "/bluetoothLEScanner.log")



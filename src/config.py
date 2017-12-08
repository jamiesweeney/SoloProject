import os

#-------------------------------------------------------------#
#-- Directories --#
# Base directory
BASE_DIR = os.path.dirname(os.path.realpath(__file__))

# Camera modules directory 
CAMERA_DIR = os.path.join(BASE_DIR + "/camera")

# Credentials directory
CREDS_DIR = os.path.join("/home/pi/.credentials/")

# Django front-end demo directory
DEMO_DIR = os.path.join(BASE_DIR + "/display_demo")

# Log directies
LOG_DIR = os.path.join(BASE_DIR + "/logs")
REPORTERS_LOG_DIR = os.path.join(LOG_DIR + "/reporters")
SCANNERS_LOG_DIR = os.path.join(LOG_DIR + "/scanners")
SENSORS_LOG_DIR = os.path.join(LOG_DIR + "/sensors")

# Reporter directory
REPORTERS_DIR = os.path.join(BASE_DIR + "/reporters")

# Scanners directory
SCANNERS_DIR = os.path.join(BASE_DIR + "/scanners")

# Sensors directory
SENSORS_DIR = os.path.join(BASE_DIR + "/sensors")

# Setup directory
SETUP_DIR = os.path.join(BASE_DIR + "/setup")


#-------------------------------------------------------------#
#-- Credential files --#
BLUETOOTH_BUCKET_CREDENTIALS = os.path.join(CREDS_DIR + "/bluetoothBucket.json")


#-------------------------------------------------------------#
#-- Log Files --#
# Reporters logs
BLUETOOTH_REPORTER_LOG = os.path.join(REPORTERS_LOG_DIR + "/bluetoothReporter.log")

# Scanner logs
BLUETOOTH_SCANNER_LOG = os.path.join(SCANNERS_LOG_DIR + "/bluetoothScanner.log")
BLUETOOTHLE_SCANNER_LOG = os.path.join(SCANNERS_LOG_DIR + "/bluetoothLEScanner.log")

# Sensor logs
TEMPERATURE_SENSOR_LOG = os.path.join(SCANNERS_LOG_DIR + "/temperatureSensor.log")


#-------------------------------------------------------------#
#-- Setup Scripts --# 
BLUETOOTH_SETUP_SCRIPT = os.path.join(SETUP_DIR + "/setupBluetooth.sh")


#-------------------------------------------------------------#
#-- Google Storage Variables --#
BLUETOOTH_BUCKET = "bluetoothscanner"
ROOM_NO = "070"


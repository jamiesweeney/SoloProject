import os


#-- Directories --#
# Base directory
BASE_DIR = os.path.dirname(os.path.realpath(__file__))

# Camera modules directory 
CAMERA_DIR = os.path.join(BASE_DIR + "/camera") 

# Django front-end demo directory
DEMO_DIR = os.path.join(BASE_DIR + "/display_demo")

# Log directies
LOG_DIR = os.path.join(BASE_DIR + "/logs")
REPORTERS_LOG_DIR = os.path.join(LOG_DIR + "/reporters")
SCANNER_LOG_DIR = os.path.join(LOG_DIR + "/scanners")

# Reporter directory
REPORTERS_DIR = os.path.join(BASE_DIR + "/reporters")

# Scanners directory
SCANNERS_DIR = os.path.join(BASE_DIR + "/scanners")

# Sensors directory
SENSORS_DIR = os.path.join(BASE_DIR + "/sensors")

# Setup directory
SETUP_DIR = os.path.join(BASE_DIR + "/setup")


#-- Log Files --#
# Reporters logs
BLUETOOTH_REPORTER_LOG = os.path.join(REPORTERS_LOG_DIR + "/bluetoothReporter.log")

# Scanner logs
BLUETOOTH_SCANNER_LOG = os.path.join(SCANNERS_LOG_DIR + "/bluetoothScanner.log")
BLUETOOTHLE_SCANNER_LOG = os.path.join(SCANNERS_LOG_DIR + "/bluetoothLEScanner.log")


#-- Startup Scripts --# 
BLUETOOTH_SETUP_SCRIPT = os.path.join(SETUP_DIR + "/setupBluetooth.sh")


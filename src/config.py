import os

#-------------------------------------------------------------#
#-- Directories --#

# Source code directory
SRC_DIR = os.path.dirname(os.path.realpath(__file__))

# Base directory
BASE_DIR = SRC_DIR.rstrip("/src")

# Camera modules directory 
CAMERA_DIR = os.path.join(SRC_DIR + "/camera")

# Credentials directory
CREDS_DIR = os.path.join("/home/pi/.credentials/")

# Darknet object detection directory
DARKNET_DIR = "/home/pi/darknet-nnpack/"

# Django front-end demo directory
DEMO_DIR = os.path.join(SRC_DIR + "/display_demo")

# Log directies
LOG_DIR = os.path.join(BASE_DIR + "/logs")
CAMERA_LOG_DIR = os.path.join(LOG_DIR + "/camera")
CAMERA_OUT_LOG_DIR = os.path.join(CAMERA_LOG_DIR + "/out")
CAMERA_RAW_LOG_DIR = os.path.join(CAMERA_LOG_DIR + "/raw")
REPORTERS_LOG_DIR = os.path.join(LOG_DIR + "/reporters")
SCANNERS_LOG_DIR = os.path.join(LOG_DIR + "/scanners")
SENSORS_LOG_DIR = os.path.join(LOG_DIR + "/sensors")

# Reporter directory
REPORTERS_DIR = os.path.join(SRC_DIR + "/reporters")

# Scanners directory
SCANNERS_DIR = os.path.join(SRC_DIR + "/scanners")

# Sensors directory
SENSORS_DIR = os.path.join(SRC_DIR + "/sensors")

# Setup directory
SETUP_DIR = os.path.join(SRC_DIR + "/setup")


#-------------------------------------------------------------#
#-- Credential Files --#
GOOGLE_CREDENTIALS = os.path.join(CREDS_DIR + "/googleCreds.json")


#-------------------------------------------------------------#
#-- Darknet YOLO Files --#
DARKNET_DATA_FILE = DARKNET_DIR + "cfg/voc.data"
DARKNET_CFG_FILE = DARKNET_DIR + "cfg/tiny-yolo-voc.cfg"
DARKNET_WEIGHTS_FILE = DARKNET_DIR + "tiny-yolo-voc.weights"

DARKNET_IMAGE = DARKNET_DIR + "testing.jpg"

#-------------------------------------------------------------#
#-- Log Files --#

# Reporters logs
BLUETOOTH_REPORTER_LOG = os.path.join(REPORTERS_LOG_DIR + "/bluetoothReporter.log")
CAMERA_REPORTER_LOG = os.path.join(REPORTERS_LOG_DIR + "/cameraReporter.log")
TEMPERATURE_REPORTER_LOG = os.path.join(REPORTERS_LOG_DIR + "/temperatureReporter.log")


# Scanner logs
BLUETOOTH_SCANNER_LOG = os.path.join(SCANNERS_LOG_DIR + "/bluetoothScanner.log")
BLUETOOTHLE_SCANNER_LOG = os.path.join(SCANNERS_LOG_DIR + "/bluetoothLEScanner.log")

# Sensor logs
TEMPERATURE_SENSOR_LOG = os.path.join(SENSORS_LOG_DIR + "/temperatureSensor.log")


#-------------------------------------------------------------#
#-- Setup Scripts --# 
BLUETOOTH_SETUP_SCRIPT = os.path.join(SETUP_DIR + "/setupBluetooth.sh")


#-------------------------------------------------------------#
#-- Google Storage Variables --#
BLUETOOTH_BUCKET = "bluetoothscanner"
CAMERA_BUCKET = "cameradetector"
TEMPERATURE_BUCKET = "temperaturesensor"
ROOM_NO = "070"


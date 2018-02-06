import os

#-------------------------------------------------------------#
#-- Directories --#

# Source code directory
SRC_DIR = os.path.dirname(os.path.realpath(__file__))

# Base directory
BASE_DIR = SRC_DIR.rstrip("/src")

# Sensors directory
SENSOR_DIR = os.path.join(SRC_DIR + "/sensors")

# Credentials directory
CREDS_DIR = os.path.join("/home/pi/.credentials/")

# Darknet object detection directory
DARKNET_DIR = "/home/pi/darknet-nnpack/"

# Log directories
LOG_DIR = os.path.join(BASE_DIR + "/logs")
REPORTER_LOG_DIR = os.path.join(LOG_DIR + "/reporter")
SENSORS_LOG_DIR = os.path.join(LOG_DIR + "/sensors")
CAMERA_LOG_DIR = os.path.join(SENSORS_LOG_DIR + "/camera")
BLUETOOTH_LOG_DIR = os.path.join(SENSORS_LOG_DIR + "/bluetooth")
CAMERA_OUT_LOG_DIR = os.path.join(CAMERA_LOG_DIR + "/out")
CAMERA_RAW_LOG_DIR = os.path.join(CAMERA_LOG_DIR + "/raw")

# Reporter directory
REPORTER_DIR = os.path.join(SRC_DIR + "/reporter")

# Setup directory
SETUP_DIR = os.path.join(SRC_DIR + "/setup")

#-------------------------------------------------------------#
#-- Darknet YOLO Files --#
DARKNET_DATA_FILE = DARKNET_DIR + "cfg/voc.data"
DARKNET_CFG_FILE = DARKNET_DIR + "cfg/tiny-yolo-voc.cfg"
DARKNET_WEIGHTS_FILE = DARKNET_DIR + "tiny-yolo-voc.weights"
DARKNET_IMAGE = DARKNET_DIR + "testing.jpg"

#-------------------------------------------------------------#
#-- Log Files --#

# Reporters logs
REPORTER_LOG = os.path.join(REPORTER_LOG_DIR + "reporter.log")

# Sensor logs
BLUETOOTH_SCANNER_LOG = os.path.join(SCANNERS_LOG_DIR + "/bluetoothScanner.log")
BLUETOOTHLE_SCANNER_LOG = os.path.join(SCANNERS_LOG_DIR + "/bluetoothLEScanner.log")


#-------------------------------------------------------------#
#-- Setup Scripts --#
BLUETOOTH_SETUP_SCRIPT = os.path.join(SETUP_DIR + "/setupBluetooth.sh")

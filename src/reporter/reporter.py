import select
import subprocess
import os
import time
import sys
import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import argparse
import threading
import csv
from multiprocessing import Process, Queue
from sensors import cameraDetection, bluetoothScanner, bluetoothLEScanner
import config
import google.cloud.storage
import json
import urllib2


def monitor(mon_type, detection_dict, det_args):

    output_queue = Queue()
    #det_args = det_args + (output_queue)

    # Set scanner thread vars
    if (mon_type == "BT"):
        name = 'blutooth_scanner'
        target = bluetoothScanner.start
    elif (mon_type  == "BTLE"):
        name = 'blutoothle_scanner'
        target = bluetoothLEScanner.start_ble
    elif (mon_type == "CAMERA"):
        name = 'camera_monitor'
        target = cameraDetection.start_detection

    # Initialise and run detector thread
    detector_thread = threading.Thread( name=name,
                                       target=target,
                                       args=det_args + (output_queue,) )
    detector_thread.start()

    # While detector is running and queue isn't empty, load detections into dictionary
    while(detector_thread.isAlive()):
        time.sleep(0.5)
        while not (output_queue.empty()):
            current_detect = output_queue.get()
            detection_dict.add(current_detect)


# Class for thread safe storing / reading of devices
class DeviceDictionary:

    # Initialise with decay time
    def __init__(self, decay_time):
        self.mutex = threading.Lock()
        self.devices = {}
        self.decay_time = decay_time

    # Add to dictionary, smoothing rssi value if necessary
    def add(self, entry):

        time_arrived = entry[0]
        address = entry[1]
        rssi = entry[2]

        address = address.lower()

        # Get mutex
        self.mutex.acquire()
        current_time = time.time()

        # If alreading present in list
        if (address in self.devices):
            # And has not decayed - smooth rssi value for entry
            if (int(self.devices[address][0]) >= (current_time - self.decay_time)):
                new_rssi = (float(self.devices[address][1]) + float(rssi))/float(2)
                self.devices[address] = [time_arrived, new_rssi]
            # And has decayed - just add new entry
            else:
                self.devices[address] = [time_arrived, rssi]
        # If not present just add
        else:
            self.devices[address] = [time_arrived, rssi]

        # Release mutex
        self.mutex.release()

    # Read from dictionary, excluding and deleting values that should decay
    def read(self):

        # Get mutex
        self.mutex.acquire()

        # Minimum time for non-decay
        min_time = time.time() - self.decay_time

        #Iterate over all devices, and filter out any that have decayed
        for device in self.devices.keys():
            if (int(self.devices[device][0]) < int(min_time)):
                del self.devices[device]

        #Release and return
        return_dict = self.devices
        self.mutex.release()
        return return_dict


# Class for thread safe storing / reading of camera output
class CameraOutput:

    # Initialise
    def __init__(self):
        self.mutex = threading.Lock()
        self.people = 0

    # Update the people count
    def add(self, output):


        print (str(output))
        # Get mutex
        self.mutex.acquire()
        current_time = time.time()

        # Update people count with new prediction, smoothing result
        new_people = ( float(self.people) + float(len(output)) ) / float(2)
        self.people = new_people

        # Release mutex
        self.mutex.release()

    # Read the people count
    def read(self):

        self.mutex.acquire()
        people = self.people
        self.mutex.release()

        return people


cycle_period = 60
image_period = 20
report_period = 30
hash_addrs = False
log_output = True
timeout = 86400
detection_dict = None
push = True
decay_time = 120

#-- Make sure sudo --#
if os.getuid() != 0:
    print("Failed - You need to run as sudo")
    sys.exit(-1)


#-- Setup Bluetooth device --#
cmd = str(config.BLUETOOTH_SETUP_SCRIPT)
setup = subprocess.Popen(cmd, shell=True)
setup.wait()

if (setup.returncode != 0):
    print ("Failed - Could not setup bluetooth device")
    sys.exit(-1)


#-- Initialise thread safe dictionary for bluetooth devices --#
device_dict = DeviceDictionary(decay_time)
camera_output = CameraOutput()


# Initialise bluetooth monitor thread
bluetooth_monitor_thread = threading.Thread( name = 'bluetooth_monitor',
                                            target = monitor,
                                            args = ("BT", device_dict, (cycle_period, hash_addrs, log_output, timeout)))

# Initialise bluetooth LE monitor thread
bluetoothle_monitor_thread = threading.Thread( name = 'bluetoothle_monitor',
                                            target = monitor,
                                            args = ("BTLE", device_dict, (image_period, hash_addrs, log_output, timeout)))

# Initialise camera monitor thread
camera_monitor_thread = threading.Thread( name = 'camera_monitor',
                                        target = monitor,
                                        args = ("CAMERA", camera_output, (cycle_period, log_output, log_output, timeout)))

print ("starting")
# Start monitor threads
bluetoothle_monitor_thread.start()
bluetooth_monitor_thread.start()
camera_monitor_thread.start()


# Setup post request data
host = os.getenv("REPORT_SERVER_HOST")
print (host)
api_ext = "/api/v1/pi-reports/add"
print (api_ext)
address = host + api_ext
roomID = os.getenv("REPORT_ROOM_ID")

post_data = {"auth" : "BLANK_KEY", "roomID" : roomID, "time" : None, "people" : None, "devices" : None}

# Start reporting
while (bluetooth_monitor_thread.isAlive() or bluetoothle_monitor_thread.isAlive() or camera_monitor_thread.isAlive()):

    print ("BT - " + str(bluetooth_monitor_thread.isAlive()))
    print ("BTLE - " + str(bluetoothle_monitor_thread.isAlive()))
    print ("CAMERA - " + str(camera_monitor_thread.isAlive()))

    temp_devices = device_dict.read()
    temp_people = camera_output.read()

    output = {"devices" : len(temp_devices), "people" : temp_people}
    print (str(output))

    # Fill in report post data
    post_data["time"] = time.time()
    post_data["people"] = temp_people
    post_data["devices"] = len(temp_devices)

    # Post data to server
    req = urllib2.Request(address)
    req.add_header('Content-Type', 'application/json')
    response = urllib2.urlopen(req, json.dumps(post_data))
    time.sleep(report_period)


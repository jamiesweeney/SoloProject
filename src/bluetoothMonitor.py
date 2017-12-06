''' bluetoothMonitor.py
    Contains a script used for starting a bluetooth + bluetooth LE scan and printing reports

    Args:
        period      -period to update report in seconds
        c_period    -period to scan for each cycle in seconds
        hash        -hash addresses or not
        log         -log output or not
        timeout     -total timeout value, when to stop scanning and reporting
        decay_time  -time for a device to decay from memory


    Jamie Sweeney
    2017/18 Solo Project
'''

#-- Imports --#
import select
import subprocess
import time
import sys
import datetime
import os
import myconstants
import argparse
import threading
from scanners import bluetoothScanner, bluetoothLEScanner
from multiprocessing import Process, Queue

#-- Class for thread safe dictionary for holding devices --#
class DeviceDictionary:
    def __init__(self, decay_time):
        self.mutex = threading.Lock()
        self.devices = {}
        self.decay_time = decay_time

    #-- Add to dictionary, smoothing rssi value if necessary --#
    def add(self, time_arrived, address, rssi):
        address = address.lower() 
       
        # Get mutex
        self.mutex.acquire()
        current_time = time.time()

        # If alreading present in list
        if (address in self.devices):
            # And has not decayed - smooth rssi value for entry
            if (self.devices[address][0] >= (current_time - self.decay_time)):
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

    #-- Read from dictionary, excluding and deleting values that should decay --#
    def read(self):

        # Get mutex
        self.mutex.acquire()

        # Minimum time for non-decay
        min_time = time.time() - self.decay_time

        #Iterate over all devices, and filter out any that have decayed
        for device in self.devices.keys():
            if (self.devices[device][0] < min_time):
                del self.device[device]

        #Release and return
        return_dict = self.devices
        self.mutex.release()
        return return_dict

#-- Worker thread for collecting scanner output and adding to device dictionary --#
def bluetooth_monitor(scanner, devices, cycle_period, hash_addrs, log_out, timeout):

    # Queue to load devices into
    device_queue = Queue()

    # Set scanner thread vars
    if (scanner == myconstants.BT_SCANNER):
        name = 'blutooth_scanner'
        target = bluetoothScanner.start
    elif (scanner == myconstants.BTLE_SCANNER):
        name = 'blutoothle_scanner'
        target = bluetoothLEScanner.start_ble
    else:
        name = target = None

    # Init and run scanner thread
    scanner_thread = threading.Thread( name=name,
                                       target=target,
                                       args=(cycle_period, hash_addrs, log_out, timeout, device_queue))
    scanner_thread.start()

    # While scanner thread is running and queue isn't empty, load devices into dictionary
    while(scanner_thread.isAlive()):
        time.sleep(0.5)
        while not (device_queue.empty()):
            current_device = device_queue.get()
            devices.add(current_device[0], current_device[1], current_device[2])

    return

#-- Make sure sudo --#
if os.getuid() != 0:
    print("Failed - You need to run as sudo")
    sys.exit(-1)

#-- Collect arguments --#
parser = argparse.ArgumentParser()
parser.add_argument('--period', type=int, help='period to update report', default = 20)
parser.add_argument('--c_period', type=int, help='period to scan for', default = 20)
parser.add_argument('--hash', type=bool, help='option to hash addresses of devices', default = False)
parser.add_argument('--log', type=bool, help='option to log addresses of devices', default = True)
parser.add_argument('--timeout', type=int, help='timeout option for scanning in seconds', default = 60)
parser.add_argument('--decay_time', type=int, help='time at which devices decay from dictionary', default = 60)
args = parser.parse_args()

#-- Setup bluetooth --#
print ("Running setup")
cmd = myconstants.BT_SETUP_SCRIPT
setup = subprocess.Popen(cmd, shell=True)
setup.wait()

#-- If failed exit --#
if (setup.returncode != 0):
    print ("Failed - could not setup bluetooth device")
    sys.exit(-1)
print ("-Setup success")

#-- Initialise thread safe dictionary --#
device_dict = DeviceDictionary(args.decay_time)

#-- Initialise bluetooth monitor thread --#
bluetooth_monitor_thread = threading.Thread( name='bluetooth_monitor',
      				       target=bluetooth_monitor,
                                       args=( myconstants.BT_SCANNER, device_dict, args.c_period,
                                              args.hash, args.log, args.timeout))

#-- Initialise bluetooth LE monitor thread --#
bluetoothle_monitor_thread = threading.Thread( name='bluetoothle_monitor',
                                      target=bluetooth_monitor,
                                      args=( myconstants.BTLE_SCANNER, device_dict, args.c_period,
                                             args.hash, args.log, args.timeout))
bluetoothle_monitor_thread.start()
bluetooth_monitor_thread.start()

#-- Start reporting --#
while (bluetooth_monitor_thread.isAlive() or bluetoothle_monitor_thread.isAlive() or True):
    time.sleep(args.period)
    
    print (". . . . .")
    print ("BT Monitor OK - " + str(bluetooth_monitor_thread.isAlive()))
    print ("BTLE Monitor OK - " + str(bluetoothle_monitor_thread.isAlive()))
    print("Time                 Address        RSSI")
    
    temp_devices = device_dict.read()
    for device in temp_devices:
        print(temp_devices[device][0] + "    " + str(device) + "     " + str(temp_devices[device][1]))

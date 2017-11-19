# Jamie Sweeney
# bluetoothMonitorManager.py - Stats the process of monitoring bluetooth devices

import select
import subprocess
import time
import sys
import datetime
import os
import myconstants
import argparse
import threading


#DeviceDictionary - Thread safe dictionary for holding devices
class DeviceDictionary: 

    #Mutex to ensure it is thread-safe
    mutex = threading.Lock()
    #Device list
    devices = {}
    #Timeout of devices in seconds
    timeout = 300

    def __init__(self, timeout):
        if timeout != None:
            self.timeout = timeout

    def add(self, time_arrived, address, rssi):
        #Get mutex
        self.mutex.acquire()
        current_time = time.time()
        print(time_arrived, address, rssi)
        if (address in self.devices):
	    if (self.devices[address][0] >= (current_time - self.timeout)):	    
                new_rssi = (float(self.devices[address][1]) + float(rssi))/float(2)
                self.devices[address] = [time_arrived, new_rssi]
            else:
                self.devices[address] = [time_arrived, rssi]
        else:
            self.devices[address] = [time_arrived, rssi]
        self.mutex.release()

    def read(self):
        #Get mutex
        self.mutex.acquire()
        min_time = time.time() - self.timeout
        for device in self.devices.keys():
            if (self.devices[device][0] < min_time):
                del self.device[device]

        #Release and return
        self.mutex.release()
        return self.devices

#bluetooth_monitor - worker thread for collecting scanner output and adding to device dictionary
def bluetooth_monitor(scanner, devices, do_hash, do_log):
    scanner_thread = subprocess.Popen(("sudo python " + scanner + " --hash " + do_hash + " --log " + do_log)
                                        , stdout=subprocess.PIPE
                                        , shell=True)
    
    reader = select.poll()
    reader.register(scanner_thread.stdout,select.POLLIN)
    
    print ("started scanner")
    while(True):
        print ("in loop")
  	time.sleep(0.5)
        if (reader.poll(1) == None):
            output_str = scanner_thread.stdout.readline()
            print("checking " + str(output_str))
	    while (output_str != None):
                output = output_str.replace('\n', '').split(' ')
                if (output != ['']):
            	    if (output[1] != "[INFO]"):
                	devices.add(output[0], output[1], output[2])
        else:
            print("skipping")


# Make sure sudo
if os.getuid() != 0:
    print("Failed - You need to run as sudo")
    sys.exit(-1)

# Default values
DEFAULT_PERIOD = 20.0
DEFAULT_HASH = "False"
DEFAULT_LOG = "True"
DEFAULT_TIMEOUT = 180


#Collect arguments
parser = argparse.ArgumentParser()
parser.add_argument('--period', type=int, help='period to update report', default = DEFAULT_PERIOD)
parser.add_argument('--hash', type=str, help='option to hash addresses of devices', default = DEFAULT_HASH)
parser.add_argument('--log', type=str, help='option to log addresses of devices', default = DEFAULT_LOG)
parser.add_argument('--time', type=int, help='timeout option for scanning in seconds', default = DEFAULT_TIMEOUT)
args = parser.parse_args()

# Run setup script
print ("Running setup")
cmd = myconstants.BT_SETUP_SCRIPT
setup = subprocess.Popen(cmd, shell=True)
setup.wait()

# If failed exit
if (setup.returncode != 0):
    print ("Failed - could not setup bluetooth device")
    sys.exit(-1)
print ("-Setup success")


#Initialise thread safe dictionary
device_dict = DeviceDictionary(args.time)

#Initialise bluetooth monitor thread
bluetooth_monitor = threading.Thread(name='bluetooth_monitor', target=bluetooth_monitor, args=(myconstants.BTLE_SCANNER, device_dict, args.hash, args.log))
bluetooth_monitor.start()

#Start reporting
while (True):
    time.sleep(args.period)
    print("----New Report----")
    temp_devices = device_dict.read()
    for device in temp_devices:
        print("Time                 Address                     RSSI")
        print(temp_devices[device][0] + "    " + str(device) + "     " + str(temp_devices[device][1]))


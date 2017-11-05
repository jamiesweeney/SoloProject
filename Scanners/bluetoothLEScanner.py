# Jamie Sweeney '17/18 Solo Project
# bluetoothLEScannery.py
# This file contains modules used for scanning for nearby bluetooth low-energy devices
#   
# Args:
#   --period int    Time to scan for each time
#   --hash bool     Hash MAC addresses or not


#Imports
import argparse
from bluepy.btle import Scanner, DefaultDelegate
import os
import sys
import datetime
import hashlib
#Do this to get other python files in the project directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from myconstants import BTLE_LOG


#Prints a log entry to file
def printToLog(printString):

    #Get current time
    time = datetime.datetime.now()
    time_string = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(BTLE_LOG, "a+") as f:
        f.write(time_string + " " + printString + '\n')


#Class which defines how each discovery is handles 
class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, device, isNewDev, isNewData):
        if (hash_addrs):
            device.addr = hashlib.sha224(device.addr.replace(":", "")).hexdigest()
        log_string = device.addr + " " + (str)(device.rssi)
        printToLog(log_string)


#   -- MAIN -- 

#Default values for scanning variables
period = 120         #Time to scan for each time (this number represents x where x*1.25 = time in seconds)
hash_addrs = False  #Hash MAC addresses or not

#Constants
log_start_str = "[INFO] Bluetooth LE Scan Started"
log_end_str = "[INFO] Bluetooth LE Scan Finished"

#Collect arguments
parser = argparse.ArgumentParser()
parser.add_argument('--period', type=int, help='period to update report')
parser.add_argument('--hash', type=bool, help='option to hash addresses of devices')
args = parser.parse_args()

if (args.period != None):
    period = args.period

if (args.hash != None):
    hash_addrs = args.hash


#Scan
printToLog(log_start_str)
scanner = Scanner().withDelegate(ScanDelegate())
scanner.scan(period)
printToLog(log_end_str)

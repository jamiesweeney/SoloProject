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
import timeit
import sys
import datetime
import time
import hashlib
#Do this to get other python files in the project directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from myconstants import BTLE_LOG


#Prints a log entry to file
def printToLog(printString):

    #Get current time
    time_string = str(int(time.time()))
    if (log_addrs):
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
log_addrs = False   #Log MAX addresses or not

#Constants
log_start_str = "[INFO] Bluetooth LE Scan Started"
log_end_str = "[INFO] Bluetooth LE Scan Finished"

#Collect arguments
parser = argparse.ArgumentParser()
parser.add_argument('--period', type=int, help='period to update report')
parser.add_argument('--hash', type=str, help='option to hash addresses of devices')
parser.add_argument('--log', type=str, help='option to log addresses of devices')
parser.add_argument('--time', type=int, help='option to timeout scanning after certain amount of seconds')
args = parser.parse_args()
args = vars(args)

if (args['period'] != None):
    period = args['period']

if (args['hash'] == 'True'):
    hash_addrs = True

if (args['log'] == 'True'):
    log_addrs = True

if (args['time'] != None):
    timeout = args['time']

#Scan
printToLog(log_start_str)
scanner = Scanner().withDelegate(ScanDelegate())

start = timeit.default_timer()
while (((timeit.default_timer() - start) < timeout) or timeout == 0):
    scanner.scan(period)
printToLog(log_end_str)


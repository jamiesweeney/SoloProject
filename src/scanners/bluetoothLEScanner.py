''' bluetoothLEScanner.py
    Contains functions used for collecting nearby bluetooth low energy devices
    The only function that should be called from outside this module is start() which
    will start the bluetooth LE scan with the specified parameters

    Invoking this file as a script will call the start() function

    Jamie Sweeney
    2017/18 Solo Project
'''

#-- Imports --#
import argparse
from bluepy.btle import Scanner, DefaultDelegate
import os
import timeit
import sys
import datetime
import time
import hashlib
# Do this to get other python files in the project directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from myconstants import BTLE_LOG

#-- Initiates scanning process with specified arguments --#
def start(cycle_period=20, hash_addrs=False, log_out=False, timeout=180, device_queue=None):
    ''' Initiates the scanning process with specified arguments
            cycle_period    - time of one scanning cycle (start/scan/stop)
            hash_addrs      - anonymise addresses or not
            log_out         - log output or not
            timeout         - time to stop scanning after
            device_queue    - device list to add new devices to
    '''
    dev_id = 0
    log_start_str = "[INFO] Bluetooth LE Scan Started"
    log_end_str = "[INFO] Bluetooth LE Scan Finished"

    #Scan
    start_time = timeit.default_timer()
    if (log_out):
        print_to_log(log_start_str)
    scanner = Scanner().withDelegate(ScanDelegate(hash_addrs, log_out, device_queue))
    while ((((timeit.default_timer()) - start) < timeout) or timeout == 0):
        scanner.scan(cycle_period)
    if (log_out):
        print_to_log(log_end_str)
    return

#-- Prints to the specified log file --#
def print_to_log(log_str):
    with open(BTLE_LOG, "a+") as f:
        f.write(log_str)

#-- Class which defines how each discovery is handles --#
class ScanDelegate(DefaultDelegate):
    def __init__(self, hash_addrs, log_out, device_queue):
        self.hash_addrs = hash_addrs
        self.log_out = log_out
        self.device_queue = device_queue
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, device, isNewDev, isNewData):
        # Get discovery vars
        time = str(int(time.time()))
        addr = device.addr
        rssi = device.rssi

        # Hash address if required
        if (self.hash_addrs):
            addr = hashlib.sha224(addr.replace(":", "")).hexdigest()

        # Add to device queue
        if (self.device_queue not None):
            self.device_queue.put(time, addr, rssi)

        #Log string
        if (self.log_out):
            log_str = str(time) + " " + str(addr) + " " + str(rssi) + '\n'
            print_to_log(log_str)

# If called as a script, just call start function
start()

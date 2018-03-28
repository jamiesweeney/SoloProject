''' bluetoothLEScanner.py
    Contains functions used for collecting nearby bluetooth low energy devices
    The only function that should be called from outside this module is start_ble() which
    will start the bluetooth LE scan with the specified parameters

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

#-- Do this to get other python files in the project directory --#
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import BLUETOOTHLE_SCANNER_LOG

#-- Initiates scanning process with specified arguments --#
def start_ble(cycle_period=20, hash_addrs=False, log_out=False, timeout=180, device_queue=None):
    ''' Initiates the scanning process with specified arguments
            cycle_period    - time of one scanning cycle (start/scan/stop)
            hash_addrs      - anonymise addresses or not
            log_out         - log output or not
            timeout         - time to stop scanning after
            device_queue    - device list to add new devices to
    '''
    log_start_str = "[INFO] Bluetooth LE Scan Started\n"
    log_end_str = "[INFO] Bluetooth LE Scan Finished\n"


    # Create scanner object with scanner delegate
    scan_del = ScanDelegate(hash_addrs, log_out, device_queue)
    scanner = Scanner().withDelegate(scan_del)

    # Scan start
    if (log_out):
        print_to_log(log_start_str)

    scan_loop(scanner, cycle_period, timeout)

    # Scan end
    if (log_out):
        print_to_log(log_end_str)


#-- Performs a scan loop --#
def scan_loop(scanner, cycle_period, timeout):
    start_time = timeit.default_timer()

    # Keep doing scans until timeout is reached
    while ((((timeit.default_timer()) - start_time) < timeout) or timeout == 0):
        try:
            scanner.scan(timeout=cycle_period) 
        except Exception as exc:
            print ("ERROR STARTING BTLE SCAN, exception:")
            print (exc)


#-- Prints to the specified log file --#
def print_to_log(log_str):
    try:
        with open(BLUETOOTHLE_SCANNER_LOG, "a+") as f:
            f.write(log_str)
    except Exception as exc:
        print ("ERROR WRITING TO FILE, exception:")
        print (exc)


#-- Will hash an address --#
def hash_address(address):

    if (address == None or address == ""):
        return None

    # Remove ':' then hash
    address = address.replace(":", "")
    new_addr = hashlib.sha224(address).hexdigest()
    return new_addr


#-- Will print a discovery to log --#
def log_discovery(device):
    log_str = device[0] + " " + device[1] + " " + device[2]


#-- Class which defines how each discovery is handles --#
class ScanDelegate(DefaultDelegate):

    # Initialise and set class vars
    def __init__(self, hash_addrs, log_out, device_queue):
        self.hash_addrs = hash_addrs
        self.log_out = log_out
        self.device_queue = device_queue
        DefaultDelegate.__init__(self)

    # Handles a new device discovery
    def handleDiscovery(self, device, isNewDev, isNewData):

        # Get discovery vars
        disc_time = str(int(time.time()))
        addr = device.addr
        rssi = device.rssi

        # Hash address if required
        if (self.hash_addrs):
            addr = hash_address(addr)

        # Create device object
        device = [disc_time, addr, rssi]

        # Add to device queue
        if (self.device_queue != None):
            self.device_queue.put(device)

        # Log device
        if (self.log_out):
            log_discovery(device)

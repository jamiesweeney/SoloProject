# Jamie Sweeney '17/18 Solo Project
# bluetoothScannery.py
# This file contains modules used for scanning for nearby bluetooth devices
#
# Args:
#   --period int    Time to scan for each time
#   --hash bool     Hash MAC addresses or not


#Imports
import argparse
import traceback
import os
import sys
import struct
import bluetooth._bluetooth as bluez
import bluetooth
import datetime
import time
import hashlib
#Do this to get other python files in the project directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from myconstants import BT_LOG


#Prints a log entry to file
def printToLog(printString):
    #Get current time
    time_string = str(int(time.time()))
    if (log_addrs):
    	with open(BT_LOG, "a+") as f:
            f.write(time_string + " " + printString + '\n')


#Sets up the bluetooth adapter to scan
def setup_bluetooth():

    #Open bluetooth device
    try:
        bt_device = bluez.hci_open_dev(dev_id)
    except Exception as e:
        errorMsg("Error accessing bluetooth device:", e)

    #Read the inquiry mode
    try:
        mode = read_inquiry_mode(bt_device)
    except Exception as e:
        errorMsg("Error reading inquiry mode:", e)

    #Write inquiry mode
    if mode != 1:
        try:
            result = write_inquiry_mode(bt_device, 1)
            if result != 0:
                errorMsg("Error while setting inquiry mode:", None)
        except Exception as e:
            errorMsg("Error writing inquiry mode:", e)

    #Return bluetooth device if setup sucessful
    return bt_device


#Performs the device inquiry process
def device_inquiry(sock):

    # save current filter
    old_filter = sock.getsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, 14)

    # perform a device inquiry on bluetooth device #0
    # The inquiry should last 8 * 1.28 = 10.24 seconds
    # before the inquiry is performed, bluez should flush its cache of
    # previously discovered devices
    filtr = bluez.hci_filter_new()
    bluez.hci_filter_all_events(filtr)
    bluez.hci_filter_set_ptype(filtr, bluez.HCI_EVENT_PKT)
    sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, filtr )

    max_responses = 255
    cmd_pkt = struct.pack("BBBBB", 0x33, 0x8b, 0x9e, period, max_responses)
    bluez.hci_send_cmd(sock, bluez.OGF_LINK_CTL, bluez.OCF_INQUIRY, cmd_pkt)

    #While still scanning
    done = False
    while not done:
        pkt = sock.recv(255)
        ptype, event, plen = struct.unpack("BBB", pkt[:3])

        #Enquiry result with rssi
        if event == bluez.EVT_INQUIRY_RESULT_WITH_RSSI:
            pkt = pkt[3:]
            nrsp = bluetooth.get_byte(pkt[0])
            for i in range(nrsp):
                addr = bluez.ba2str( pkt[1+6*i:1+6*i+6] )
                if (hash_addrs):
                        addr =  hashlib.sha224(addr.replace(":", "")).hexdigest()
                rssi = bluetooth.byte_to_signed_int(
                        bluetooth.get_byte(pkt[1+13*nrsp+i]))
                print_device(addr, rssi)

        #Enquiry result without rssi
        elif event == bluez.EVT_INQUIRY_RESULT:
            pkt = pkt[3:]
            nrsp = bluetooth.get_byte(pkt[0])
            for i in range(nrsp):
                addr = bluez.ba2str( pkt[1+6*i:1+6*i+6] )
                if (hash_addrs):
                    addr = hashlib.sha224(addr.replace(":","")).hexdigest()
                print_device(addr, None)

        #On finish
        elif event == bluez.EVT_INQUIRY_COMPLETE:
            done = True

        #Status update?
        elif event == bluez.EVT_CMD_STATUS:
            status, ncmd, opcode = struct.unpack("BBH", pkt[3:7])
            if status != 0:
                done = True

    # restore old filter
    sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, old_filter )
    return

#Reads the inquiry mode of the bluetooth adapter
def read_inquiry_mode(sock):
    """returns the current mode, or -1 on failure"""
    # save current filter
    old_filter = sock.getsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, 14)

    # Setup socket filter to receive only events related to the
    # read_inquiry_mode command
    flt = bluez.hci_filter_new()
    opcode = bluez.cmd_opcode_pack(bluez.OGF_HOST_CTL,
            bluez.OCF_READ_INQUIRY_MODE)
    bluez.hci_filter_set_ptype(flt, bluez.HCI_EVENT_PKT)
    bluez.hci_filter_set_event(flt, bluez.EVT_CMD_COMPLETE);
    bluez.hci_filter_set_opcode(flt, opcode)
    sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, flt )

    # first read the current inquiry mode.
    bluez.hci_send_cmd(sock, bluez.OGF_HOST_CTL,
            bluez.OCF_READ_INQUIRY_MODE )

    pkt = sock.recv(255)

    status,mode = struct.unpack("xxxxxxBB", pkt)
    if status != 0: mode = -1

    # restore old filter
    sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, old_filter )
    return mode


#Writes the inquiry mode of the bluetooth adapter
def write_inquiry_mode(sock, mode):
    """returns 0 on success, -1 on failure"""
    # save current filter
    old_filter = sock.getsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, 14)

    # Setup socket filter to receive only events related to the
    # write_inquiry_mode command
    flt = bluez.hci_filter_new()
    opcode = bluez.cmd_opcode_pack(bluez.OGF_HOST_CTL,
            bluez.OCF_WRITE_INQUIRY_MODE)
    bluez.hci_filter_set_ptype(flt, bluez.HCI_EVENT_PKT)
    bluez.hci_filter_set_event(flt, bluez.EVT_CMD_COMPLETE);
    bluez.hci_filter_set_opcode(flt, opcode)
    sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, flt )

    # send the command!
    bluez.hci_send_cmd(sock, bluez.OGF_HOST_CTL,
            bluez.OCF_WRITE_INQUIRY_MODE, struct.pack("B", mode) )

    pkt = sock.recv(255)

    status = struct.unpack("xxxxxxB", pkt)[0]

    # restore old filter
    sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, old_filter )
    if status != 0: return -1
    return 0


#Creates device found log and prints it
def print_device(addr, rssi):

    #Get name of address if not hashing addresses
    name = None
    if not (hash_addrs):
        name = bluetooth.lookup_name(addr, 100)

    #Makes string
    log_string = addr
    if (rssi):
        log_string = log_string +  " " + (str)(rssi)
    if (name):
        log_string + log_string + " " + name

    printToLog(log_string)


#Prints error messeges and exits the program
def errorMsg(text, error):
    print (text)
    print (error)
    sys.exit(1)

#   -- MAIN --

#Default values for scanning variables
dev_id = 0          #ID of the bluetooth device to use
period = 20         #Time to scan for each time (this number represents x where x*1.25 = time in seconds)
hash_addrs = False  #Hash MAC addresses or not
log_addrs = False   #Log MAC addresses of not

#Constants
log_start_str = "[INFO] Bluetooth Scan Started"
log_end_str = "[INFO] Bluetooth Scan Finished"

#Collect arguments
parser = argparse.ArgumentParser()
parser.add_argument('--period', type=int, help='period to update report')
parser.add_argument('--hash', type=str, help='option to hash addresses of devices')
parser.add_argument('--log', type=str, help='option to log addresses of devices')
args = parser.parse_args()
args = vars(args)

if (args['period'] != None):
    period = args['period']

if (args['hash'] == 'True'):
    hash_addrs = True

if (args['log'] == 'True'):
    log_addrs = True

#Attempt setup
bt_device = setup_bluetooth()
if not (bt_device):
    sys.exit(1)

print (period)
print (hash_addrs)
print (log_addrs)

#Start scanning
printToLog(log_start_str)
device_inquiry(bt_device)
printToLog(log_end_str)


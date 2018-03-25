''' bluetoothScanner.py
    Contains functions used for collecting nearby bluetooth devices
    The only function that should be called from outside this module is start() which
    will start the bluetooth scan with the specified parameters

    Invoking this file as a script will call the start() function

    Jamie Sweeney
    2017/18 Solo Project
'''

#-- Imports --#
import argparse
import traceback
import os
import sys
import struct
import bluetooth._bluetooth as bluez
import bluetooth
import datetime
import time
import timeit
import hashlib
# Do this to get other python files in the project directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import BLUETOOTH_SCANNER_LOG
dev_id=0

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
    log_start_str = "[INFO] Bluetooth Scan Started\n"
    log_end_str = "[INFO] Bluetooth Scan Finished\n"

    # Attempt setup
    bt_device = setup_bluetooth()
    if not (bt_device):
        sys.exit(1)

    #Scan
    start_time = timeit.default_timer()
    if (log_out):
        print_to_log(log_start_str)
    while ((((timeit.default_timer()) - start_time) < timeout) or timeout == 0):
        device_inquiry(bt_device, cycle_period, hash_addrs, log_out, device_queue)
    if (log_out):
        print_to_log(log_end_str)
    return

#-- Sets up the bluetooth adapter to scan --#
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

#-- Reads the inquiry mode of the bluetooth adapter --#
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

#-- Writes the inquiry mode of the bluetooth adapter --#
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

#-- Performs the device inquiry process --#
def device_inquiry(sock, cycle_period, hash_addrs, log_out, device_queue):

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
    cmd_pkt = struct.pack("BBBBB", 0x33, 0x8b, 0x9e, int(cycle_period/1.25), max_responses)
    bluez.hci_send_cmd(sock, bluez.OGF_LINK_CTL, bluez.OCF_INQUIRY, cmd_pkt)

    #While still scanning
    done = False
    while not done:
        sock.settimeout(5)
        try:
            pkt = sock.recv(255)
        except:
            break
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
                register_device(addr, rssi, log_out, device_queue)

        #Enquiry result without rssi
        elif event == bluez.EVT_INQUIRY_RESULT:
            pkt = pkt[3:]
            nrsp = bluetooth.get_byte(pkt[0])
            for i in range(nrsp):
                addr = bluez.ba2str( pkt[1+6*i:1+6*i+6] )
                if (hash_addrs):
                    addr = hashlib.sha224(addr.replace(":","")).hexdigest()
                register_device(addr, None, log_out, device_queue)

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

#-- Registers device with system and logs it --#
def register_device(addr, rssi, log_out, device_queue):

    print (addr)

    #Get current time
    current_time = str(int(time.time()))

    #Add to device queue
    if (device_queue != None):
        device_queue.put([current_time, addr, rssi])

    #Log string
    if (log_out):
        log_str = str(current_time) + "," + str(addr) + "," + str(rssi) + '\n'
        print_to_log(log_str)

#-- Prints to the specified log file --#
def print_to_log(log_str):
    with open(BLUETOOTH_SCANNER_LOG, "a+") as f:
        f.write(log_str)

#-- Prints error messeges and exits the program --#
def errorMsg(text, error):
    print (text)
    print (error)
    sys.exit(1)

#start()

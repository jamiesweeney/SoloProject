# performs a simple device inquiry, followed by a remote name request of each
# discovered device

import traceback
import os
import sys
import struct
import bluetooth._bluetooth as bluez
import bluetooth
import datetime

def printpacket(packet):
    for c in packet:
        sys.stdout.write("%02x " % struct.unpack("B",c)[0])
    print() 


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

def device_inquiry(sock, time):
    
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

    duration = time
    max_responses = 255
    cmd_pkt = struct.pack("BBBBB", 0x33, 0x8b, 0x9e, duration, max_responses)
    bluez.hci_send_cmd(sock, bluez.OGF_LINK_CTL, bluez.OCF_INQUIRY, cmd_pkt)

    results = {}

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
                rssi = bluetooth.byte_to_signed_int(
                        bluetooth.get_byte(pkt[1+13*nrsp+i]))
                results[addr] = rssi
                print_device(addr, rssi)

        #Enquiry result without rssi
        elif event == bluez.EVT_INQUIRY_RESULT:
	    pkt = pkt[3:]
            nrsp = bluetooth.get_byte(pkt[0])
            for i in range(nrsp):
                addr = bluez.ba2str( pkt[1+6*i:1+6*i+6] )
                print_device(addr, None)

        #On finish
        elif event == bluez.EVT_INQUIRY_COMPLETE:
            done = True

        #Status update?
        elif event == bluez.EVT_CMD_STATUS:
            status, ncmd, opcode = struct.unpack("BBH", pkt[3:7])
            if status != 0:
                printpacket(pkt[3:7])
                done = True
                
    # restore old filter
    sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, old_filter )

    return results

def print_device(addr, rssi):

    time = datetime.datetime.now()
    time_string = time.strftime("%Y-%m-%d %H:%M:%S")

    name = bluetooth.lookup_name(addr, 100)

    log_string = time_string + " " + addr


    if (rssi):
        log_string = log_string +  " " + (str)(rssi)

    if (name):
	log_string + log_string + " " + name
 
    print (log_string)
    log_file.flush()

def collect_devices():

    dev_id = 0
    devices = {}

    #Open bluetooth device
    try:
        bt_device = bluez.hci_open_dev(dev_id)
    except Exception as e:
        errorMsg("Error accessing bluetooth device:", e)

    #Read the inquiry mode
    try:
        mode = read_inquiry_mode(bt_device)
    except Exception as e:
        traceback.print_exc()
        errorMsg("Error reading inquiry mode:", e)
    
    #Write inquiry mode
    if mode != 1:
        try:
            result = write_inquiry_mode(bt_device, 1)
            if result != 0:
                print("Error while setting inquiry mode:")
        except Exception as e:
            errorMsg("Error writing inquiry mode:", e)

    #Start scanning
    print ("[INFO] Bluetooth Scan Started")
    log_file.flush()

    #Perform equiry
    while (True):
    	device_inquiry(bt_device,20)

def errorMsg(text, error):
    print (text)
    print (error)
    sys.exit(1)

log_file = open("bluetoothScanner.log", "a")
sys.stdout = log_file
collect_devices()
print ("[INFO] Bluetooth Scan Finished")
log_file.close()


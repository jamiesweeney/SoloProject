# Jamie Sweeney
# bluetoothMonitor - Starts bluetooth scanners and gives a periodic summary from log files

import subprocess
import time
import sys
import datetime
import os
import myconstants
import argparse

#Default values
period = 20

#Make sure sudo
if os.getuid() != 0:
    print("Failed - You need to run as sudo")
    sys.exit(-1)    

#Collect arguments
parser = argparse.ArgumentParser()
parser.add_argument('--period', type=int, help='period to update report')
args = parser.parse_args()

if ('period' in args):
    period = period



#Run setup script
print ("Running setup")
cmd = myconstants.BT_SETUP_SCRIPT
setup = subprocess.Popen(cmd , shell=True)
setup.wait()

#If failed exit
if (setup.returncode != 0):
    print ("Could not setup bluetooth device")
    sys.exit(-1)
print ("-Setup success")

#Start scanners
print ("Starting bluetooth scanner")
bluetooth_scanner = subprocess.Popen(("python " + myconstants.BT_SCANNER), shell=True)

print ("Starting bluetooth LE scanner")
bluetoothle_scanner = subprocess.Popen("python " + myconstants.BTLE_SCANNER, shell=True)

#Start loop
while (True):
    time.sleep(period)
    print ("")
    print ("NEW REPORT")
    
    #Reset lists
    bluetooth_devices = {}
    bluetoothle_devices = {}

    #Check scanners are still running
    if (bluetooth_scanner.poll() == None):
        print ("--Bluetooth Scanner OK")
        print ("--Bluetooth LE Scanner OK")

    #Define a limit to read
    limit = datetime.datetime.now() - datetime.timedelta(minutes=5)
    limit_string = limit.strftime("%Y-%m-%d %H:%M:%S")

    #Open bluetooth log file, read in reversed order
    bluetooth_log = open(myconstants.BT_LOG, 'r+')
    for line in reversed(bluetooth_log.readlines()):

        #Skip info lines
        if (line.startswith("[INFO]")):
             continue

	#Make a time limit to consider log entries until
        logtime = line.split(" ")[0] + " " + line.split(" ")[1]
        if (logtime < limit_string):
	    break

        #Get device info
	address = line.split(" ")[2]
        rssi = int(line.split(" ")[3][:-1])

        #Add to list if not present, if it is just store the rssi
        if (address not in bluetooth_devices):
            bluetooth_devices[address] = []
        bluetooth_devices[address].append(rssi)         
    
    #Average rssi value
    for device in bluetooth_devices:
        average_rssi = sum(bluetooth_devices[device]) / len(bluetooth_devices[device]) 
        bluetooth_devices[device] = average_rssi 
    
    #Close log
    bluetooth_log.close()


    #Open bluetooth LE log file, read in reversed order
    bluetoothle_log = open(myconstants.BTLE_LOG, "r+")
    for line in reversed(bluetoothle_log.readlines()):

        #Skip info lines
        if (line.startswith("[INFO]")):
             continue

        #Make a time limit to consider log entries until
        logtime = line.split(" ")[0] + " " + line.split(" ")[1]
        if (logtime < limit_string):
            break

        #Get device info
        address = line.split(" ")[2]
        rssi = int(line.split(" ")[3][:-1])

        #Add to list if not present, if it is just store the rssi
        if (address not in bluetoothle_devices):
            bluetoothle_devices[address] = []
        bluetoothle_devices[address].append(rssi)

    #Average rssi value
    for device in bluetoothle_devices:
        average_rssi = sum(bluetoothle_devices[device]) / len(bluetoothle_devices[device])
        bluetoothle_devices[device] = average_rssi

    #Close log
    bluetoothle_log.close()
  
    #Join results
    all_devices = {}
    for device in bluetooth_devices:
        all_devices[device] = [bluetooth_devices[device], None]

    for device in bluetoothle_devices:
        if device not in all_devices:
            all_devices[device] = [None, bluetoothle_devices[device]]
        else:
            all_devices[device][1] = bluetoothle_devices[device]

    #Print results
    print ("Address\t\t\t BT-RSSI\t BTLE-RSSI")
    for device in all_devices:
	print (device + "\t" + str(all_devices[device][0]) + "\t\t" + str(all_devices[device][1]))    
print (all_devices)

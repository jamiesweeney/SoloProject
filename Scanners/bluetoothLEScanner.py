from bluepy.btle import Scanner, DefaultDelegate
import os
import sys
import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from myconstants import BTLE_LOG

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, device, isNewDev, isNewData):
	
	time = datetime.datetime.now()
	time_string = time.strftime("%Y-%m-%d %H:%M:%S")	

	log_string = time_string + " " + device.addr + " " + (str)(device.rssi)
        
        log_file = open(BTLE_LOG, "a+")
        log_file.write((log_string + '\n'))
        log_file.close()

#Time to loop for
time = 120.0

#Log file
log_file = open(BTLE_LOG, "a+")
log_file.write(("[INFO] Bluetooth LE Scan Started" + '\n'))
log_file.close()

#Start scanning
scanner = Scanner().withDelegate(ScanDelegate()) 
while (True):
	scanner.scan(time)

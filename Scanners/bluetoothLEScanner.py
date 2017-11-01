from bluepy.btle import Scanner, DefaultDelegate
import sys
import datetime

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, device, isNewDev, isNewData):
	
	time = datetime.datetime.now()
	time_string = time.strftime("%Y-%m-%d %H:%M:%S")	

	log_string = time_string + " " + device.addr + " " + (str)(device.rssi)

	print (log_string)
	log_file.flush()


#Time to loop for
time = 120.0

#Log file
log_file = open("bluetoothLEScanner.log", "a")
sys.stdout = log_file

#Start scanning
print ("[INFO] Bluetooth LE Scan Started")
scanner = Scanner().withDelegate(ScanDelegate()) 
while (True):
	scanner.scan(time)

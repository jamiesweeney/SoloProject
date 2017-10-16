import subprocess

#Create sub-process and wait to finish
scan_process = subprocess.Popen(["sudo", "hcitool","scan"], stdout=subprocess.PIPE)
scan_process.wait()

#Retrieve output and remove loading string
output = scan_process.communicate()[0]
output = output.split('\n')
del output[0]
output[:] = [item for item in output if item]

devices = {}

#Split each device into ["MAC", "DeviceName"]
for device in output:
    devices[device.split('\t')[1]] = device.split('\t')[2]

#Print
print (devices)

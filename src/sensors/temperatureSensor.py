''' temperatureSensor.py
    Contains functions used for collecting temperature information
    Functions:
        get_cpu_temperature - returns the cpu thermometer reading

    Jamie Sweeney
    2017/18 Solo Project
'''

#-- Imports --#
import commands

#-- Returns the cpu temperature as float --#
def get_cpu_temperature():
    #Get temperature reading
    temp = commands.getstatusoutput("/opt/vc/bin/vcgencmd measure_temp")[1]

    #Remove extra text
    temp = temp.split("=")[1]
    temp = temp.split("'")[0]

    return float(temp)

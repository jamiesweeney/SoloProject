''' temperatureSensor.py
    Contains functions used for collecting temperature information

    Jamie Sweeney
    2017/18 Solo Project
'''

#-- Imports --#
import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import commands
from config import TEMPERATURE_SENSOR_LOG

#-- Returns the cpu temperature as float --#
def get_cpu_temperature(log_out=False):
    ''' Gets the current cpu temperature with specified arguments
            log_out         - log output or not
    '''
    #Get temperature reading
    temp = commands.getstatusoutput("/opt/vc/bin/vcgencmd measure_temp")[1]

    #Remove extra text
    temp = temp.split("=")[1]
    temp = temp.split("'")[0]

    log_str = str(int(time.time())) +"," + str(temp) + "\n"

    if (log_out):
        print_to_log(log_str)

    return float(temp)

#-- Prints to the specified log file --#
def print_to_log(log_str):
    with open(TEMPERATURE_SENSOR_LOG, "a+") as f:
        f.write(log_str)

get_cpu_temperature(log_out=True)

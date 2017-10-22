""" temperateSensor.py
    This module contains methods for collecting temperature sensor data
    
    J Sweeney 2017
"""

import commands



def get_cpu_temperature():
    """ Gets the current reading from the cpu thermometer
    
	Returns:
            float - temperature in celcius
    """	
    
    #Get temperature reading
    temp = commands.getstatusoutput("/opt/vc/bin/vcgencmd measure_temp")[1]
    
    #Remove extra text
    temp = temp.split("=")[1]
    temp = temp.split("'")[0]

    return float(temp)    


print (get_cpu_temperature())

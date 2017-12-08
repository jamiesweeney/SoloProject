import picamera
import subprocess
import time
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DARKNET_DIR, DARKNET_IMAGE, DARKNET_DATA_FILE, DARKNET_CFG_FILE, DARKNET_WEIGHTS_FILE

def start_detection():

    camera = picamera.PiCamera()
    camera.hflip = True
    camera.vflip = True

    camera.capture(DARKNET_IMAGE)
    call_str = "./darknet detector test " + DARKNET_DATA_FILE +" "+ DARKNET_CFG_FILE +" "+ DARKNET_WEIGHTS_FILE + " " + DARKNET_IMAGE
    a = subprocess.Popen(call_str, cwd=DARKNET_DIR, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = a.communicate()
    obj_list = out[0].split('\n')[1:-1] 
    person_list = []
    for obj in obj_list:
        obj_split = obj.split(': ')
        if obj_split[0] == "person":
            person_list += [obj]

    print obj_list
    print person_list
    print str(len(person_list))

start_detection()
        

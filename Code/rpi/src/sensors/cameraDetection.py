import picamera
import subprocess
import time
import os
import shutil
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DARKNET_DIR, DARKNET_IMAGE, DARKNET_DATA_FILE, DARKNET_CFG_FILE, DARKNET_WEIGHTS_FILE, CAMERA_OUT_LOG_DIR, CAMERA_RAW_LOG_DIR

def start_detection(cycle_period=20, log_out=False, log_raw=False, timeout=180, output_queue=None):
    # Mininum of 20 seconds cycle period
    if (cycle_period < 20):
        cycle_period = 10

    # Darknet YOLO call string
    call_str = "./darknet detector test " + DARKNET_DATA_FILE + " " + DARKNET_CFG_FILE + " " + DARKNET_WEIGHTS_FILE  + " " + DARKNET_IMAGE


    # Setup pi camera
    camera = picamera.PiCamera()
    camera.hflip = True
    camera.vflip = True

    start_t = time.time()
    wait_period = 0

    while ((time.time() - timeout) < start_t):
        time.sleep(wait_period)

        loop_s = time.time()

        # Take image
        camera.capture(DARKNET_IMAGE)
        time_c = str(time.time()).split(".")[0]

        # Log output
        if (log_raw):
            log_f = CAMERA_RAW_LOG_DIR + "/" + time_c + ".jpg"
            shutil.copy(DARKNET_IMAGE, log_f)

        # Call object detection and get output
        obj_det_thread = subprocess.Popen(call_str, cwd=DARKNET_DIR, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = obj_det_thread.communicate()
        obj_list = out[0].split('\n')[1:-1]

        # Extract persons
        person_list = []
        for obj in obj_list:
            obj_split = obj.split(': ')
            if obj_split[0] == "person":
                person_list += [obj]

        if (output_queue != None):
            output_queue.put(person_list)

        # Log output
        if (log_out):
            log_f = CAMERA_OUT_LOG_DIR + "/" + time_c + ".png"
            shutil.copy(DARKNET_DIR + "predictions.png", log_f)

        loop_diff = cycle_period - (time.time() - loop_s)
        if (loop_diff > 0):
            wait_period = loop_diff
        else:
            wait_period = 0

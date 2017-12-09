import select
import subprocess
import os
import time
import sys
import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import argparse
import threading
import csv
from multiprocessing import Process, Queue
from camera import cameraDetection
import config
import google.cloud.storage

def start_camera_report(period, log, timeout, push):

    # Set up google storage bucket
    if (push == True):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(config.GOOGLE_CREDENTIALS)
        storage_client = google.cloud.storage.Client()
        bucket = storage_client.get_bucket(config.CAMERA_BUCKET)
        
    output_queue = Queue()

    name = "camera_detector"
    target = cameraDetection.start_detection

    detector_thread = threading.Thread( name=name,
                                       target=target,
                                       args=(period, log, log, timeout, output_queue))
    detector_thread.start()

    while (detector_thread.isAlive()):
        time.sleep(period)
        out_list = output_queue.get()

        if (push == True):
            send_to_storage(out_list, log, bucket)


#-- Sends the report to external storage --#
def send_to_storage(data, log, bucket):
    log_time = str(time.time()).split(".")[0]
    log_f = config.REPORTERS_LOG_DIR + "/" + "cam_out" + ".csv" 

    if (log == True):
        print_to_log("New Report at time: " + log_time + "\n")

    # Generate csv file        
    with open(log_f, 'wb') as myfile:
        wr = csv.writer(myfile)
        for person in data:
            wr.writerow(person.split(":"))

            if (log == True):
                print_to_log("    " + str(person) + "\n")

    # Upload csv file
    blob = bucket.blob(config.ROOM_NO + "/" + log_time)
    blob.upload_from_filename(log_f)
    os.remove(log_f)
            
    return

    

#-- Prints to the specified log file --#
def print_to_log(log_str):
    with open(config.CAMERA_REPORTER_LOG, "a+") as f:
        f.write(log_str)

start_camera_report(20, True, 100, True)

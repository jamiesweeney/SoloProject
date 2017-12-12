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
from sensors import temperatureSensor
import config
import google.cloud.storage

def start_temperature_report(period, log, timeout, push):

    # Set up google storage bucket
    if (push == True):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(config.GOOGLE_CREDENTIALS)
        storage_client = google.cloud.storage.Client()
        bucket = storage_client.get_bucket(config.TEMPERATURE_BUCKET)
        


    start_t = time.time()

    while ((start_t + timeout) > time.time()):
        time.sleep(period)

        print (". . . . .")
        temperature = temperatureSensor.get_cpu_temperature(log_out=log)

        print (str(temperature))
        
        if (push == True):
            send_to_storage(temperature, log, bucket)


#-- Sends the report to external storage --#
def send_to_storage(data, log, bucket):
    log_time = str(time.time()).split(".")[0]
    log_f = config.REPORTERS_LOG_DIR + "/" + "temp_out" + ".csv" 

    if (log == True):
        print_to_log("New Report at time: " + log_time + "\n")

    # Generate csv file        
    with open(log_f, 'wb') as myfile:
        wr = csv.writer(myfile)
        wr.writerow([str(data)])

        if (log == True):
            print_to_log("    " + str(data) + "\n")

    # Upload csv file
    blob = bucket.blob(config.ROOM_NO + "/" + log_time)
    blob.upload_from_filename(log_f)
    os.remove(log_f)
            
    return

    

#-- Prints to the specified log file --#
def print_to_log(log_str):
    with open(config.TEMPERATURE_REPORTER_LOG, "a+") as f:
        f.write(log_str)


#-- Make sure sudo --#
if os.getuid() != 0:
    print("Failed - You need to run as sudo")
    sys.exit(-1)

#-- Collect arguments --#
parser = argparse.ArgumentParser()
parser.add_argument('--period', type=int, help='period to update report', default = 60)
parser.add_argument('--log', type=bool, help='option to log data', default = True)
parser.add_argument('--timeout', type=int, help='timeout option in seconds', default = 600)
parser.add_argument('--push', type=bool, help='option to push data to google storage', default = True)

args = parser.parse_args()

start_temperature_report(args.period, args.log, args.timeout, args.push)

import picamera
import subprocess
import time


DN_DIR = "/home/pi/darknet-nnpack/"
DATA_FILE = DN_DIR + "cfg/voc.data"
CFG_FILE = DN_DIR + "cfg/tiny-yolo-voc.cfg"
WEIGHTS_FILE = DN_DIR + "tiny-yolo-voc.weights"

camera = picamera.PiCamera()
camera.sharpness = 0
camera.contrast = 0
camera.brightness = 50
camera.saturation = 0
camera.ISO = 0
camera.video_stabilization = False
camera.exposure_compensation = 0
camera.exposure_mode = 'auto'
camera.meter_mode = 'average'
camera.awb_mode = 'auto'
camera.image_effect = 'none'
camera.color_effects = None
camera.rotation = 0
camera.hflip = True
camera.vflip = True
camera.crop = (0.0, 0.0, 1.0, 1.0)

camera.capture( DN_DIR + "testing.jpg")
call_str = "./darknet detector test " + DATA_FILE +" "+ CFG_FILE +" "+ WEIGHTS_FILE + " testing.jpg"
a = subprocess.Popen(call_str, cwd=DN_DIR, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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

        

import picamera
import subprocess
import time


DN_DIR = "/home/pi/darknet-nnpack/"
DATA_FILE = DN_DIR + "cfg/voc.data"
CFG_FILE = DN_DIR + "cfg/tiny-yolo-voc.cfg"
WEIGHTS_FILE = DN_DIR + "tiny-yolo-voc.weights"
'''
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
'''


#while (True):
#camera.capture( DN_DIR + "testing.jpg")
call_str = "./darknet detector test " + DATA_FILE +" "+ CFG_FILE +" "+ WEIGHTS_FILE + " testing.jpg"
a = subprocess.Popen(call_str, cwd=DN_DIR, shell=True, stderr=subprocess.PIPE)
#    print a.communicate()
 #   time.sleep(2)

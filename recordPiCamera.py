from picamera import PiCamera
from time import sleep
import io

#Apro piCamera con risoluzione di 320x240 a 30fps
#E registro un video per 60 secondi
camera = PiCamera();
camera.resolution = (320,240);
camera.framerate = 30;
camera.start_recording("myvideo3.h264");
camera.wait_recording(60);
camera.stop_recording();

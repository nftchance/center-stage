import cv2

from Detector import *

detector = Detector()

# detector.process_video('cpi.mp4')
detector.process_webcam()
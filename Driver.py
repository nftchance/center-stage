import cv2

from Detector import *

detector = Detector(use_cuda=True)

detector.process_video('cpi.mp4')
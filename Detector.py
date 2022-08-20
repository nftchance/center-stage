import cv2
import numpy
import time
from imutils.video import FPS


class Detector:
    def __init__(self, use_cuda=False):
        self.face_model = cv2.dnn.readNetFromCaffe(
            'res10_300x300_ssd_iter_140000.prototxt', 'res10_300x300_ssd_iter_140000.caffemodel')

        if use_cuda:
            self.face_model.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            self.face_model.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

    def process_frame(self):
        blob = cv2.dnn.blobFromImage(
            self.img, 1.0, (300, 300), (104.0, 177.0, 123.0), swapRB=False, crop=False)
        self.face_model.setInput(blob)
        detections = self.face_model.forward()

        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.5:
                box = detections[0, 0, i, 3:7] * \
                    numpy.array([self.w, self.h, self.w, self.h])
                (startX, startY, endX, endY) = box.astype("int")
                cv2.rectangle(self.img, (startX, startY),
                              (endX, endY), (0, 255, 0), 2)

        return detections

    def process_image(self, img_name):
        self.img = cv2.imread(img_name)
        (self.h, self.w) = self.img.shape[:2]

        self.process_frame()

        cv2.imshow('Output', self.img)
        cv2.waitKey(0)

    def process_video(self, video_name):
        cap = cv2.VideoCapture(video_name)

        (ret, self.img) = cap.read()
        (self.h, self.w) = self.img.shape[:2]

        while cap.isOpened():
            (ret, self.img) = cap.read()

            if not ret:
                break

            self.process_frame()

            cv2.imshow('img', self.img)

            k = cv2.waitKey(30) & 0xff
            if k == 27:
                break

        cap.release()
        cv2.destroyAllWindows()

    def process_webcam(self):
        cap = cv2.VideoCapture(0)

        (ret, self.img) = cap.read()
        (self.h, self.w) = self.img.shape[:2]

        while cap.isOpened():
            (ret, self.img) = cap.read()

            if not ret:
                break

            self.process_frame()

            cv2.imshow('img', self.img)

            k = cv2.waitKey(30) & 0xff
            if k == 27:
                break

        cap.release()
        cv2.destroyAllWindows()

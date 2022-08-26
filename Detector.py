import cv2
import numpy
import pyvirtualcam
import time

from threading import Thread

font = cv2.FONT_HERSHEY_SIMPLEX

DEFAULTS = {
    'confidence': 0.65,
    'target_face_percentage': 80,
    'zoom': 1.0,
}

class FaceDetector(Thread):
    def __init__(self, cascade_path, confidence=DEFAULTS['confidence'], target_face_percentage=DEFAULTS['target_face_percentage'], debug=False):
        self.debug = debug
        self.confidence = confidence
        self.target_face_percentage = target_face_percentage

        self.cap = cv2.VideoCapture(0)

        self.pref_width = 1280
        self.pref_height = 720
        self.pref_fps_in = 30
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.pref_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.pref_height)
        self.cap.set(cv2.CAP_PROP_FPS, self.pref_fps_in)

        # Query final capture device values (may be different from preferred settings).
        self.w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps_in = self.cap.get(cv2.CAP_PROP_FPS)
        print(f'Webcam capture started ({self.w}x{self.h} @ {self.fps_in}fps)')

        self.face_cascade = cv2.CascadeClassifier(cascade_path)

        self.prev_frame_time = 0
        self.new_frame_time = 0

        self.face_location = None

        self.face_model = cv2.dnn.readNetFromCaffe(
            'models/res10_300x300_ssd_iter_140000.prototxt',
            'models/res10_300x300_ssd_iter_140000.caffemodel'
        )

        self.cyp = None
        self.cxp = None

        self.easing = 0.05

        self.zoom = DEFAULTS['zoom']
        self.zoom_decay = 0

    def get_faces(self, img):
        blob = cv2.dnn.blobFromImage(
            img, 1.0, (300, 300), (104.0, 177.0, 123.0), swapRB=False, crop=False)
        self.face_model.setInput(blob)
        detections = self.face_model.forward()

        faces = []

        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > self.confidence:
                box = detections[0, 0, i, 3:7] * \
                    numpy.array([self.w, self.h, self.w, self.h])

                (startX, startY, endX, endY) = box.astype("int")
                faces.append((startX, startY, endX - startX, endY - startY))

        return faces

    def zoom_at(self, img, zoom=DEFAULTS['zoom'], angle=0, coord=None):
        # focus on the center of previous frame + easing in the direction of the center of the face in the current image if no coord is given then use the center of the face in the current image
        if not self.cxp:
            self.cxp = coord[0]
            self.cyp = coord[1]
        
        # if coordinates aren't supplied, use the center of the image
        if coord is None:
            coord = (img.shape[1] / 2, img.shape[0] / 2)

        # ease our way towards the current value
        cx = self.cxp + (coord[0] - self.cxp) * self.easing
        cy = self.cyp + (coord[1] - self.cyp) * self.easing

        # ease the zoom in towards the target value
        zoom = self.zoom + (zoom - self.zoom) * self.easing

        # draw circle at current center
        if self.debug:
            cv2.circle(img, (int(cx), int(cy)), int(zoom), (0, 0, 255), -1)

        # get the center of the face in the previous frame
        rot_mat = cv2.getRotationMatrix2D((cx, cy), angle, zoom)
        result = cv2.warpAffine(
            img, rot_mat, img.shape[1::-1], flags=cv2.INTER_LINEAR)

        self.cxp = cx
        self.cyp = cy
        self.zoom = zoom

        return result

    def zoom_at_face(self, img, faces):
        color = (0, 0, 255)

        # if has face in frame then zoom in on face otherwise use face_location as zoom target
        if len(faces) > 0:
            color = (0, 255, 0)

            x, y, w, h = faces[0]
            self.face_location = (x, y, w, h)
            self.zoom_decay = 0.0
        else:
            self.zoom_decay = self.zoom_decay + self.easing if self.zoom_decay < 1 else 1

        # if has face location zoom in to last location
        if self.face_location:
            (x, y, w, h) = self.face_location

            # zoom in on face
            face_percentage = (h / img.shape[0]) * 100
            zoom_factor = 1 + (1 - (face_percentage / self.target_face_percentage)) - self.zoom_decay

            if zoom_factor < 1: zoom_factor = 1

            # draw rectangle around face
            if self.debug:
                cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)

            img = self.zoom_at(
                img,
                zoom=zoom_factor,
                angle=0,
                coord=(x + w / 2, y + h / 2)
            )

        return img

    def run(self):
        print('Inside run')
        fmt = pyvirtualcam.PixelFormat.BGR
        # use pvirtual came to get the frame
        with pyvirtualcam.Camera(width=int(self.w), height=int(self.h), fps=28.4, fmt=fmt) as cam:
            print(f'Using virtual camera: {cam.device}')

            while self.cap.isOpened():
                # Capture frame-by-frame
                ret, img = self.cap.read()

                if not ret:
                    break

                # faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                faces = self.get_faces(img)

                # Center the screen on the faces in the image
                img = self.zoom_at_face(img, faces)

                # Flip frame
                img = cv2.flip(img, 1) 

                if self.debug:
                    # Display the resulting frame
                    self.new_frame_time = time.time()

                    # fps will be number of frame processed in given time frame
                    # since their will be most of time error of 0.001 second
                    # we will be subtracting it to get more accurate result
                    fps = 1 / (self.new_frame_time - self.prev_frame_time)
                    self.prev_frame_time = self.new_frame_time

                    # Display FPS on frame
                    cv2.putText(img, "FPS: {:.2f}".format(
                        fps), (0, 30), font, 1, (0, 0, 255), 2, cv2.LINE_AA)
                    fps = f"{int(fps)}"

                    cv2.imshow('Center Stage' if not self.debug else '[Debug] Center Stage', img)

                    # Press Escape on keyboard to  exit
                    k = cv2.waitKey(30) & 0xff
                    if k == 27:
                        break

                    cv2.destroyAllWindows()
                else:
                    # zoom in on face
                    cam.send(img)

        self.cap.release()


def main():
    print("Stepping inside the main")
    face = FaceDetector(
        'models/haarcascade_frontalface_default.xml',
        confidence=0.5,
        target_face_percentage=50,
        debug=False
    )
    face.run()

if __name__ == '__main__':
    main()

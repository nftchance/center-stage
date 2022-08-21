import cv2
import numpy
import time

font = cv2.FONT_HERSHEY_SIMPLEX


class FaceDetector():
    def __init__(self, cascade_path, confidence=0.5, target_face_percentage=90, debug=False):
        self.debug = debug
        self.confidence = confidence
        self.target_face_percentage = target_face_percentage

        self.cap = cv2.VideoCapture(0)
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

        self.prev_frame_time = 0
        self.new_frame_time = 0

        self.face_location = None

        self.w = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.h = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

        self.face_model = cv2.dnn.readNetFromCaffe(
            'models/res10_300x300_ssd_iter_140000.prototxt',
            'models/res10_300x300_ssd_iter_140000.caffemodel'
        )

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

    def zoom_at(self, img, zoom=1, angle=0, coord=None):
        cy, cx = [i/2 for i in img.shape[:-1]
                  ] if coord is None else coord[::-1]

        rot_mat = cv2.getRotationMatrix2D((cx, cy), angle, zoom)
        result = cv2.warpAffine(
            img, rot_mat, img.shape[1::-1], flags=cv2.INTER_LINEAR)

        return result

    def zoom_at_face(self, img, faces):
        # if has face in frame then zoom in on face otherwise use face_location as zoom target
        if len(faces) > 0:
            x, y, w, h = faces[0]
            self.face_location = (x, y, w, h)

        # if has face location zoom in to last location
        if self.face_location:
            (x, y, w, h) = self.face_location

            # zoom in on face
            face_percentage = (h / img.shape[0]) * 100
            zoom_factor = 1 + \
                (1 - (face_percentage / self.target_face_percentage))

            img = self.zoom_at(
                img,
                zoom=zoom_factor,
                angle=0,
                coord=(x + w / 2, y + h / 2)
            )

        return img

    def run(self):
        while True:
            # Capture frame-by-frame
            ret, img = self.cap.read()

            if not ret:
                break

            # faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            faces = self.get_faces(img)

            # Center the screen on the faces in the image
            img = self.zoom_at_face(img, faces)

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
                    fps), (0, 90), font, 1, (0, 0, 255), 2, cv2.LINE_AA)
                fps = f"{int(fps)}"

            # zoom in on face
            cv2.imshow('img', img)

            # Press Escape on keyboard to  exit
            k = cv2.waitKey(30) & 0xff
            if k == 27:
                break

        self.cap.release()
        cv2.destroyAllWindows()


def main():
    face = FaceDetector(
        'models/haarcascade_frontalface_default.xml', 
        confidence=0.65,
        target_face_percentage=90, 
        debug=False
    )
    face.run()


if __name__ == '__main__':
    main()

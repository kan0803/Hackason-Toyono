import cv2

class FaceDetector:
    @classmethod
    def detect_face(cls, frame):
        """フレームの画像データに対して顔検出を行う"""
        # 顔検出器を初期化
        face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

        # グレースケール変換
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 顔検出
        faces = face_detector.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        # 検出された顔の座標とサイズを返す
        face_coordinates = [{"x": int(x), "y": int(y), "width": int(w), "height": int(h)} for (x, y, w, h) in faces]
        return face_coordinates
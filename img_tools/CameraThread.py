import cv2
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap

# La clase `CameraThread` captura fotogramas de una cámara y emite una señal con los datos del
# fotograma como `QImage`.
class CameraThread(QThread):
    frame_data = pyqtSignal(QImage)

    def run(self):
        """
        La función captura video desde una cámara web y convierte cada cuadro en una imagen RGB.
        """
        # El fragmento de código que proporcionó captura fotogramas desde una cámara web usando OpenCV
        # (`cv2.VideoCapture(0)`).
        capture = cv2.VideoCapture(0)
        while True:
            ret, frame = capture.read()
            if ret:
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.frame_data.emit(qt_image)
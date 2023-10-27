import sys
import cv2
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget, QPushButton

class CameraApp(QMainWindow):
    def __init__(self):
        super().__init__()

        #Tamaño del video 
        self.video_size = (640, 480)


        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)


        #Espacio donde se pondra el video alineado al centro 
        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)

        #Creo un boton  y lo conecto a la funcion star_camera
        self.start_button = QPushButton('Start Camera', self)
        self.start_button.clicked.connect(self.start_camera)

        #Ceao un layout dodne todos los elementos los coloca verticalmente organizados 
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.addWidget(self.video_label)
        self.layout.addWidget(self.start_button)
        
        
        self.video_capture = None  # Se inicializará cuando se presione el botón
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

    def start_camera(self):
        if not self.video_capture:
            self.video_capture = cv2.VideoCapture(0)
            self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.video_size[0])
            self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.video_size[1])
            self.timer.start(30)

    def update_frame(self):
        ret, frame = self.video_capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            self.video_label.setPixmap(pixmap)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CameraApp()
    window.setGeometry(100, 100, 800, 600)
    window.setWindowTitle('Camera App')
    window.show()
    sys.exit(app.exec_())

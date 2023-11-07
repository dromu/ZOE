import sys
import cv2
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen
from PyQt5.QtCore import Qt, QPoint

class CameraApp(QMainWindow):
    def __init__(self):
        super(CameraApp, self).__init__()

        self.video_capture = cv2.VideoCapture(0)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)

        self.drawing = False
        self.last_point = QPoint()

        layout = QVBoxLayout(self.central_widget)
        layout.addWidget(self.image_label)

        self.update_frame()

    def update_frame(self):
        ret, frame = self.video_capture.read()
        if ret:
            image = self.convert_frame_to_pixmap(frame)
            self.image_label.setPixmap(image)
        self.update()

    def convert_frame_to_pixmap(self, frame):
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        return pixmap

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.last_point = event.pos()

    def mouseMoveEvent(self, event):
        if self.drawing:
            painter = QPainter(self.image_label.pixmap())
            painter.setPen(QPen(Qt.blue, 2, Qt.SolidLine))
            painter.drawLine(self.last_point, event.pos())
            self.last_point = event.pos()
            self.image_label.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = CameraApp()
    main_window.show()

    sys.exit(app.exec_())

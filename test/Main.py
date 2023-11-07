import sys
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QGraphicsScene, QGraphicsView, QWidget
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt, QPointF

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.points_enabled = False

        layout = QVBoxLayout()
        layout.addWidget(self.view)

        self.button = QPushButton("Habilitar Puntos")
        self.button.clicked.connect(self.toggle_points)
        layout.addWidget(self.button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.points = []

        # Inicializar la cámara
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Actualizar el fotograma cada 30 ms

    def toggle_points(self):
        self.points_enabled = not self.points_enabled
        if self.points_enabled:
            self.button.setText("Agregar Punto")
        else:
            self.button.setText("Habilitar Puntos")

    def add_point(self, event):
        if self.points_enabled:
            x = event.scenePos().x()
            y = event.scenePos().y()
            self.points.append((x, y))
            print(f"Punto añadido en ({x}, {y})")

    def mousePressEvent(self, event):
        super(MainWindow, self).mousePressEvent(event)
        self.add_point(event)
        self.draw_points()

    def draw_points(self):
        # Limpiar la escena
        self.scene.clear()

        # Dibujar los puntos en rojo
        for point in self.points:
            ellipse_item = self.scene.addEllipse(point[0] - 5, point[1] - 5, 10, 10, Qt.red)
            ellipse_item.setFlag(ellipse_item.ItemIsMovable)

    def update_frame(self):
        # Capturar un fotograma de la cámara
        ret, frame = self.cap.read()
        if ret:
            # Dibujar puntos en el fotograma
            if self.points_enabled:
                for point in self.points:
                    cv2.circle(frame, (int(point[0]), int(point[1])), 5, (0, 0, 255), -1)

            # Convertir el fotograma de OpenCV a un formato QImage
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()

            # Mostrar el fotograma en la escena
            pixmap = QPixmap.fromImage(q_img)
            self.scene.addPixmap(pixmap)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setGeometry(100, 100, 800, 600)
    window.show()
    sys.exit(app.exec_())

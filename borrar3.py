import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap, QPainter, QColor
from PyQt5.QtCore import Qt

class MyCanvas(QGraphicsView):
    def __init__(self):
        super(MyCanvas, self).__init__()

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.imageItem = QGraphicsPixmapItem(QPixmap("tu_imagen.png"))
        self.scene.addItem(self.imageItem)

        self.lastPos = None
        self.brushSize = 20  # Tamaño del pincel

    def mouseMoveEvent(self, event):
        if self.lastPos:
            painter = QPainter(self.imageItem.pixmap())
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.setPen(Qt.transparent)
            painter.drawEllipse(self.lastPos, self.brushSize, self.brushSize)
            self.imageItem.setPixmap(self.imageItem.pixmap())
            self.lastPos = event.pos()

    def mousePressEvent(self, event):
        self.lastPos = event.pos()

    def mouseReleaseEvent(self, event):
        self.lastPos = None

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.canvas = MyCanvas()
        self.setCentralWidget(self.canvas)

        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle("Borrador con Color Transparente")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

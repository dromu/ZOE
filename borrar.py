import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QRectF


class PaintApp(QMainWindow):
    def __init__(self):
        super(PaintApp, self).__init__()

        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Paint App')

        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setSceneRect(0, 0, 800, 600)

        self.setCentralWidget(self.view)

        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)

        self.pixmap = QPixmap(800, 600)
        self.pixmap.fill(Qt.transparent)
        self.pixmap_item.setPixmap(self.pixmap)

        self.last_point = None
        self.borrando = False

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_point = event.pos()
            self.borrando = True
            self.borrar(event.pos())

    def mouseMoveEvent(self, event):
        if self.borrando:
            self.borrar(event.pos())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.borrando = False

    def borrar(self, pos):
        if self.last_point:
            painter = QPainter(self.pixmap)
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            pen = QPen(Qt.transparent)
            pen.setWidth(20)  # Ajusta el ancho del borrador según sea necesario
            painter.setPen(pen)
            painter.drawLine(self.last_point, pos)
            painter.end()

            self.last_point = pos
            self.pixmap_item.setPixmap(self.pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PaintApp()
    ex.show()
    sys.exit(app.exec_())

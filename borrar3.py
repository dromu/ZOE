import sys
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsPixmapItem, QGraphicsArrowItem, QGraphicsView
from PyQt5.QtGui import QPixmap, QPainter, QPen
from PyQt5.QtCore import Qt

class ImageWithArrows(QGraphicsView):
    def __init__(self):
        super(ImageWithArrows, self).__init__()

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # Cargar la imagen
        pixmap = QPixmap("tu_imagen.png")
        item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(item)

        # Añadir flechas a la escena
        arrow1 = QGraphicsArrowItem()
        arrow1.setLine(50, 50, 150, 150)
        self.scene.addItem(arrow1)

        arrow2 = QGraphicsArrowItem()
        arrow2.setLine(200, 200, 100, 100)
        self.scene.addItem(arrow2)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageWithArrows()
    window.show()
    sys.exit(app.exec_())

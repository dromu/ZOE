import sys
from PyQt5 import uic, QtWidgets
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QPoint
from img_tools.CameraView import ProcesadorCamara
from PyQt5.QtWidgets import QFileDialog

class DrawingBoard(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.last_point = QPoint()
        self.dibujando = False
        self.draw = False
        self.pixmap_tablero = QPixmap(1300, 850)
        self.pixmap_tablero.fill(QColor(0, 255, 0, 0))
        self.setPixmap(self.pixmap_tablero)
        self.brushColor = Qt.black
        self.brushSize = 3
        self.pen_color = Qt.black
        self.pen_size = 2

    def habEscritura(self):
        self.draw = not self.draw

    def mousePressEvent(self, event):
        if self.draw:
            self.last_point = event.pos()
            self.dibujando = True
            self.update()

    def mouseMoveEvent(self, event):
        current_point = event.pos()
        if self.dibujando and self.draw:
            painter = QPainter(self.pixmap_tablero)
            painter.setPen(QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawLine(self.last_point, current_point)
            painter.end()
            self.setPixmap(self.pixmap_tablero)
            self.repaint()
            self.last_point = current_point
            self.update()

    def mouseReleaseEvent(self, event):
        self.dibujando = False
        self.update()

    def clear(self):
        self.pixmap_tablero.fill(QColor(0, 255, 0, 0))
        self.update()

    def pincelColor(self, color):
        colores = {"blue": Qt.blue, "red": Qt.red, "green": Qt.green, "black": Qt.black, "yellow": Qt.yellow, "white": Qt.white}
        self.brushColor = colores.get(color, Qt.black)  #Color negro como predeterminado

    def pincelSize(self,tam):
        self.brushSize = tam


        
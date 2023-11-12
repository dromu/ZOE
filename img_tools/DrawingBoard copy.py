import sys
from PyQt5 import uic, QtWidgets
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QPoint
from img_tools.CameraView import ProcesadorCamara
from PyQt5.QtWidgets import QFileDialog

from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu,QAction,QFileDialog
from PyQt5.QtGui import QIcon, QImage, QPainter, QPen, QPolygon
from PyQt5.QtCore import Qt, QPoint, QRect
import sys

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
        self.drawRect  = False

        self.begin, self.destination = QPoint(), QPoint()	

    def habEscritura(self):
        self.draw = not self.draw
        print("habEscritura")
    
    def habRect(self):
        self.drawRect = not self.drawRect 

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.begin = event.pos()
            self.destination = self.begin

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.last_point = self.destination
            self.destination = event.pos()

            painter = QPainter(self.pixmap_tablero)
            painter.setPen(QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

            if self.draw:
                painter.drawLine(self.last_point, self.destination)
                painter.end()
                self.setPixmap(self.pixmap_tablero)
                self.repaint()

            elif self.drawRect:
                painter.drawRect(QRect(self.begin, self.destination).normalized())
                painter.end()
                self.setPixmap(self.pixmap_tablero)
                self.update()
           

    def mouseReleaseEvent(self, event):
        painter = QPainter(self.pixmap_tablero)
        painter.setPen(QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        
        if event.button() == Qt.LeftButton:
           
            
            if self.drawRect:
                painter.drawRect(QRect(self.begin, self.destination).normalized())
                painter.end()
                self.setPixmap(self.pixmap_tablero)
                self.repaint()

            

    # def paintEvent(self, event):
        
    #     painter = QPainter(self.pixmap_tablero)
    #     painter.setPen(QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    #     # painter.drawPixmap(self.rect(), self.pixmap_tablero, self.pixmap_tablero.rect())
        
    #     # if self.drawRect:
    #     if not self.begin.isNull() and not self.destination.isNull():
    #         #     painter.drawRect(QRect(self.last_point, self.destination).normalized())
                
    #         #     self.setPixmap(self.pixmap_tablero)
    #         if self.draw:
    #             painter.drawLine(self.last_point, self.destination)
    #             painter.end()
    #             self.setPixmap(self.pixmap_tablero)
    #             # self.repaint()
               
              


        # if self.drawRect:
        #     rect = QRect(self.begin, self.destination)
        #     painter.drawPixmap(rect, self.pixmap_tablero, rect.normalized())
        #     painter.end()
        #     self.setPixmap(self.pixmap_tablero)
            

    def clear(self):
        self.pixmap_tablero.fill(QColor(0, 255, 0, 0))
    
        self.setPixmap(self.pixmap_tablero)
        self.repaint()

    def pincelColor(self, color):
        colores = {"blue": Qt.blue, "red": Qt.red, "green": Qt.green, "black": Qt.black, "yellow": Qt.yellow, "white": Qt.white}
        self.brushColor = colores.get(color, Qt.black)  #Color negro como predeterminado

    def pincelSize(self,tam):
        self.brushSize = tam
    
    


        

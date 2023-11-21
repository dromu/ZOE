import sys
from PyQt5 import uic, QtWidgets
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor,QFont,QFontMetrics
from PyQt5.QtCore import Qt, QPoint
from img_tools.CameraView import ProcesadorCamara
from PyQt5.QtWidgets import QFileDialog, QLineEdit
from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsScene, QGraphicsLineItem

from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu,QAction,QFileDialog
from PyQt5.QtGui import QIcon, QImage, QPainter, QPen, QPolygon
from PyQt5.QtCore import Qt, QPoint, QRect, QPointF
import sys

class complementaryColor(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
                
        self.pixmap_tablero = QPixmap(1300, 850)
        self.pixmap_tablero.fill(QColor(0, 0, 0, 0))
        self.setPixmap(self.pixmap_tablero)    
        self.brushColor = Qt.black
        self.brushSize = 3
        self.pen_color = Qt.black
        self.pen_size = 2
        
        self.drawRect  = False
        self.borrador = QColor(0, 0, 0, 255)
        
        #Lineas para el texto
        self.text_input = QLineEdit(self)
        self.text_input.setGeometry(10, 10, 200, 50)
        self.text_input.hide()

        self.begin, self.destination = QPoint(), QPoint()	

            
    def habColor(self):
        self.drawRect = not self.drawRect 
        print(self.drawRect)
        self.begin, self.destination = QPoint(), QPoint()	

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.begin = event.pos()
            self.destination = self.begin
            print(self.begin, self.destination)    

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.last_point = self.destination
            self.destination = event.pos()

            print(self.last_point, self.destination)      

    def mouseReleaseEvent(self, event): #Eventos que se realizan cuando se suelta el mouse
        painter = QPainter(self.pixmap_tablero)
        painter.setPen(QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        
        if event.button() == Qt.LeftButton:
                    
            if self.drawRect:
                painter.drawRect(QRect(self.begin, self.destination).normalized())
                self.begin, self.destination = QPoint(), QPoint()	#SE actualizan las posiciones para que no hayan otros dibujos

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawPixmap(QPoint(), self.pixmap_tablero)

        if not self.begin.isNull() and not self.destination.isNull():
            if self.drawRect:
                rect = QRect(self.begin, self.destination)
                painter.drawRect(rect.normalized())

            

    
    


        

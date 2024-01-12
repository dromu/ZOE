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
        self.hideWindow = False
        self.drawElip = False
        self.drawText = False
        self.draft = False
        self.drawArrow = False
        self.colorComp = False

        self.borrador = QColor(0, 0, 0, 255)

        self.strokes = []  # Lista para almacenar los trazos realizados
        
        
        #Lineas para el texto
        self.text_input = QLineEdit(self)
        self.text_input.setGeometry(10, 10, 200, 50)
        self.text_input.hide()

        self.begin, self.destination = QPoint(), QPoint()	

    def habColor(self):
        self.colorComp = not self.colorComp
        
        #Se habilita para dibujar un recuadro 
        self.habRect()
        


    def habEscritura(self):
        self.draw = not self.draw
        self.begin, self.destination = QPoint(), QPoint()	
            
    def habRect(self):
        self.drawRect = not self.drawRect 
        self.begin, self.destination = QPoint(), QPoint()	
    
    def habElipse(self):
        self.drawElip = not self.drawElip

        print(self.drawElip)
        self.begin, self.destination = QPoint(), QPoint()	

    def habDel(self):
        self.draft= not self.draft
        self.begin, self.destination = QPoint(), QPoint()	

    def habText(self):
        self.drawText = not self.drawText
        
        if self.drawText:
            self.text_input.show()
        else:
            self.text_input.hide()

        self.begin, self.destination = QPoint(), QPoint()	

    def hideWind(self):
        self.hideWindow = not self.hideWindow

        if self.hideWindow:
            super().hide()  # Oculta el widget DrawingBoard
        else:
            super().show()  # Muestra el widget DrawingBoard
        
    

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.begin = event.pos()
            self.destination = self.begin

            if self.colorComp:
                self.clear()
                self.update()

            

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.last_point = self.destination
            self.destination = event.pos()

            painter = QPainter(self.pixmap_tablero)
            
            if self.draw:
                painter.setPen(QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                painter.drawLine(self.last_point, self.destination)
                painter.end()
                self.setPixmap(self.pixmap_tablero)
                self.repaint()

            elif self.draft:
                painter.setPen(QPen(self.borrador, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                painter.drawLine(self.last_point, self.destination)
                painter.end()
                self.setPixmap(self.pixmap_tablero)
                self.repaint()
            

    def mouseReleaseEvent(self, event): #Eventos que se realizan cuando se suelta el mouse
        painter = QPainter(self.pixmap_tablero)
        painter.setPen(QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        
        if event.button() == Qt.LeftButton:
                    
            if self.drawRect:
                
                # limpia la pantalla para evitar trazos artifciales, con ello calcula el color complementario
                if self.colorComp:
                    self.clear()
                    painter.setPen(QPen(Qt.black, 2, Qt.DashLine, Qt.RoundCap, Qt.RoundJoin))
                    self.update()

                    #Guardamos archivo de coordenadas
                    nombre_archivo = "img_tools/position.dat"
                    coordenadas = [[self.begin.x(),self.begin.y()], 
                                   [self.destination.x(), self.destination.y()]]

                    with open(nombre_archivo, 'w') as archivo:
                        archivo.write(str(coordenadas))



                painter.drawRect(QRect(self.begin, self.destination).normalized())
                self.begin, self.destination = QPoint(), QPoint()	#SE actualizan las posiciones para que no hayan otros dibujos

            elif self.drawElip:
                painter.drawEllipse(QRect(self.begin, self.destination).normalized())
                self.begin, self.destination = QPoint(), QPoint()	#SE

            elif self.drawText:
                user_text = self.text_input.text()
                font = QFont("Arial",self.brushSize+10)

                  # Obtener el rectángulo del texto para calcular el ancho
                text_rect = QFontMetrics(font).boundingRect(user_text)

                # Calcular las coordenadas para centrar el texto alrededor del punto de inicio
                x_centered = int(self.begin.x() - text_rect.width() / 2)
                y_centered = int(self.begin.y() + text_rect.height() / 2)-10

                # Dibujar el texto en el pixmap
                
                painter.setFont(font)
                painter.setPen(self.brushColor)
                painter.drawText(QPoint(x_centered, y_centered), user_text)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawPixmap(QPoint(), self.pixmap_tablero)

        if not self.begin.isNull() and not self.destination.isNull():
            if self.drawRect:
                rect = QRect(self.begin, self.destination)
                painter.drawRect(rect.normalized())

            elif self.drawElip:
                painter.drawEllipse(QRect(self.begin, self.destination).normalized())
            
    def clear(self):

        #Transparencia total 
        self.pixmap_tablero.fill(QColor(0, 0, 0, 0))
    
        self.setPixmap(self.pixmap_tablero)
        self.repaint()
        self.update()

    def pincelColor(self, color):
        colores = {"blue": Qt.blue, "red": Qt.red, "green": Qt.green, "black": Qt.black, "yellow": Qt.yellow, "white": Qt.white}
        self.brushColor = colores.get(color, Qt.black)  #Color negro como predeterminado

    def pincelSize(self,size):
        self.brushSize = size
    
    


        

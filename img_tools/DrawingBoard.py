import sys
from PyQt5 import uic, QtWidgets
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor,QFont,QFontMetrics
from PyQt5.QtCore import Qt, QPoint
from img_tools.CameraView import ProcesadorCamara
from PyQt5.QtWidgets import QFileDialog, QLineEdit

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
        self.hideWindow = False
        self.drawElip = False
        self.drawText = False
        self.draft = False

        self.borrador = QColor(0, 0, 0, 255)
        
        
        #Lineas para el texto
        self.text_input = QLineEdit(self)
        self.text_input.setGeometry(10, 10, 200, 50)
        self.text_input.hide()

        self.begin, self.destination = QPoint(), QPoint()	

    def habEscritura(self):
        self.draw = not self.draw
        self.begin, self.destination = QPoint(), QPoint()	
        print("habEscritura")
    
    def habRect(self):
        self.drawRect = not self.drawRect 
        self.begin, self.destination = QPoint(), QPoint()	
    
    def habElipse(self):
        self.drawElip = not self.drawElip
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
                painter.drawRect(QRect(self.begin, self.destination).normalized())
                self.begin, self.destination = QPoint(), QPoint()	#SE actualizan las posiciones para que no hayan otros dibujos

            if self.drawElip:
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
            
            # elif self.drawText:
            #     painter.drawText(QRect(self.begin, self.destination).normalized(), Qt.AlignCenter, "Texto en el rectángulo")
               

    def clear(self):
        self.pixmap_tablero.fill(QColor(0, 255, 0, 0))
    
        self.setPixmap(self.pixmap_tablero)
        self.repaint()
        self.update()

    def pincelColor(self, color):
        colores = {"blue": Qt.blue, "red": Qt.red, "green": Qt.green, "black": Qt.black, "yellow": Qt.yellow, "white": Qt.white}
        self.brushColor = colores.get(color, Qt.black)  #Color negro como predeterminado

    def pincelSize(self,tam):
        self.brushSize = tam
    
    


        

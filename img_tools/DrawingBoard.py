import sys
from PyQt5 import uic, QtWidgets
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor,QFont,QFontMetrics
from PyQt5.QtCore import Qt, QPoint
from img_tools.CameraView import ProcesadorCamara
from PyQt5.QtWidgets import QFileDialog, QLineEdit
from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsScene, QGraphicsLineItem
from PyQt5.QtGui import QCursor
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu,QAction,QFileDialog
from PyQt5.QtGui import QIcon, QImage, QPainter, QPen, QPolygon
from PyQt5.QtCore import Qt, QPoint, QRect, QPointF
import sys
from PyQt5.QtWidgets import QWidget, QInputDialog, QVBoxLayout
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtWidgets import QApplication, QDialog, QFormLayout, QLineEdit, QVBoxLayout, QPushButton,QMessageBox
from utils.dialogText import CustomInputDialog

class DrawingBoard(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.last_point = QPoint()
        self.dibujando = False
        self.draw = False
        self.pixmap_tablero = QPixmap(1600, 891)
        self.pixmap_tablero.fill(QColor(0, 0, 0, 0))
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
        self.txt = ""
        

        self.strokes = []  # Lista para almacenar los trazos realizados
        self.Coord   = []
        self.color   = []
        self.tamaño  = []
        
        #Lineas para el texto
        self.text_input = QLineEdit(self)
        self.text_input.setGeometry(10, 10, 200, 50)
        self.text_input.hide()

        self.begin, self.destination = QPoint(), QPoint()	
        
        self.conCtrlZ = 0
        self.posDecision = 0
        self.trazo = 0


    def disarm(self):
        self.draw       == False
        self.drawRect   == False
        self.drawElip   == False
        self.drawText   == False
        self.draft      == False
        self.colorComp  == False

    

    def habColor(self):       
        self.colorComp = not self.colorComp
        #Se habilita para dibujar un recuadro 
        if self.colorComp:
            self.brushSize = 3

        self.habRect()
        
        


    def habEscritura(self):
        
        self.draw = not self.draw
        
        # print("self.draw: ", self.draw)
        self.begin, self.destination = QPoint(), QPoint()	
        self.setCursor(QCursor(Qt.ArrowCursor))

        if self.draw:
            
            # Si deseas cargar un cursor personalizado, puedes hacerlo de la siguiente manera:
            cursor_path = 'images\icons\dibujo\lapiz2.ico'
            self.setCursor(QCursor(QPixmap(cursor_path)))
        else: 
            self.setCursor(QCursor(Qt.ArrowCursor))
            
            
    def habRect(self):
        
        self.drawRect = not self.drawRect 
        self.setCursor(QCursor(Qt.ArrowCursor))

        # print("self.drawRect: ", self.drawRect)
        self.begin, self.destination = QPoint(), QPoint()	

        if self.drawRect:
            
            self.setCursor(QCursor(Qt.CrossCursor))
            
        else: 
            self.setCursor(QCursor(Qt.ArrowCursor))
        
    
    def habElipse(self):
        self.drawElip = not self.drawElip
        self.begin, self.destination = QPoint(), QPoint()	
        self.setCursor(QCursor(Qt.ArrowCursor))
        if self.drawElip:
            
            self.setCursor(QCursor(Qt.CrossCursor))
        else: 
            self.setCursor(QCursor(Qt.ArrowCursor))

    def habDel(self):
        self.draft= not self.draft
        self.begin, self.destination = QPoint(), QPoint()	
        
        if self.draft:
            cursor_path = 'images\icons\dibujo\eraser5.ico'
            self.setCursor(QCursor(QPixmap(cursor_path)))
        else: 
            self.setCursor(QCursor(Qt.ArrowCursor))
    

    def habText(self):
        self.drawText = not self.drawText
        if self.drawText:
            
            custom_input_dialog = CustomInputDialog()
            result = custom_input_dialog.exec_()

            if result == QDialog.Accepted:
                self.texto =  custom_input_dialog.findChild(QLineEdit).text()
            else:
                self.texto = ""

            
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
            
            #LApiz
            if self.draw:
                
                painter.setPen(QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                painter.drawLine(self.last_point, self.destination)
                painter.end()
                self.setPixmap(self.pixmap_tablero)
                self.repaint()

            #Borrador
            elif self.draft:
                self.borrador = QColor(0, 0, 0, 0)
                painter.setCompositionMode(QPainter.CompositionMode_Clear)
                painter.setPen(QPen(self.borrador, 47 ,Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                painter.drawLine(self.last_point, self.destination)
                painter.end()
                self.setPixmap(self.pixmap_tablero)
                self.repaint()

            #Vector de coordenadas, color, grosor
            self.Coord.append(self.last_point)
            self.color   = self.brushColor
            self.tamaño  = self.brushSize

            
            

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
                # user_text = self.text_input.text()
                font = QFont("Arial",self.brushSize+10)

                  # Obtener el rectángulo del texto para calcular el ancho
                text_rect = QFontMetrics(font).boundingRect(self.texto)
                

                # Calcular las coordenadas para centrar el texto alrededor del punto de inicio
                x_centered = int(self.begin.x() - text_rect.width() / 2)
                y_centered = int(self.begin.y() + text_rect.height() / 2)-10

                # Dibujar el texto en el pixmap
                
                painter.setFont(font)
                painter.setPen(self.brushColor)
                painter.drawText(QPoint(x_centered, y_centered), self.texto)

            # Aqui las lineas para generar el ctrl+Z y ctrl+Y
            
        

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

    def pincelColor(self, color_hex):
        color = QColor(color_hex)
        if color.isValid():
            self.brushColor = color
        else:
            # Si el color hexadecimal no es válido, utiliza negro como color predeterminado
            self.brushColor = Qt.black#Color negro como predeterminado

    def pincelSize(self,size):
        self.brushSize = size

    



        
        



        
    
    


        

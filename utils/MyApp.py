import sys
from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget,QColorDialog
from img_tools.CameraView import ProcesadorCamara
from PyQt5.QtGui import QImage, QPixmap
import cv2 

from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu,QAction,QFileDialog
from PyQt5.QtGui import QIcon, QImage, QPainter, QPen, QPolygon, QColor
from PyQt5.QtCore import Qt, QPoint, QRect

import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QPainter, QColor
from PyQt5.QtCore import Qt, QPoint

qtCreatorFile = "gui\zoe_main.ui"  # Nombre del archivo aquí.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):

    #Constuctor 
    def __init__(self, *args, **kwargs):
        
        # Se heredan todos los parametros del file .UI
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)      #Configuracion de la interfaz grafica 
        
        ## Tablero escritura 
        # Crear un QPixmap para el tablero
        ancho = 1300
        largo = 850
        self.pixmap_tablero = QPixmap(ancho, largo)
        self.pixmap_tablero.fill(QColor(0, 255, 0,0))  # Se vuelve transparente para la escritura sobre camara
        
        # Se despliega sobre el Qlabel "tablero"
        self.tablero.setPixmap(self.pixmap_tablero)

        # Variables para seguir el trazo del ratón
        self.last_point = QPoint()
        self.dibujando = False
        self.draw = False   # hAbilitar los trazon 

        # Conectar eventos de clic y movimiento del ratón a las funciones correspondientes
        self.tablero.mousePressEvent = self.mousePressEvent
        self.tablero.mouseMoveEvent = self.mouseMoveEvent

        self.brushSize = 1
        #Funcion que hace que se habilite las escrituras 
        self.pbDot.clicked.connect(self.habEscritura)
        self.pbTrash.clicked.connect(self.clear)

        self.pen_color = Qt.black
        self.pen_size = 2

        # Crear una instancia de ProcesadorCamara
        self.procesador_camara = ProcesadorCamara()
        self.procesador_camara.iniciar_camara()

        # Conectar la señal de actualización de ProcesadorCamara a la función de actualización de la interfaz
        self.procesador_camara.senal_actualizacion.connect(self.actualizar_interfaz)

        self.estilo_original = self.pbDot.styleSheet()
        
        self.brushColor = Qt.black
        self.blueAction.triggered.connect(self.brushBlue)
        self.redAction.triggered.connect(self.brushRed)
        self.greenAction.triggered.connect(self.brushGreen)
        self.blackAction.triggered.connect(self.brushBlack)
        self.yellowAction.triggered.connect(self.brushYellow)
        self.whiteAction.triggered.connect(self.brushWhite)

        self.onepxAction.triggered.connect(self.onepx)
        self.threepxAction.triggered.connect(self.threepx)
        self.fivepxAction.triggered.connect(self.fivepx)
        self.sevenpxAction.triggered.connect(self.sevenpx)
        self.ninepxAction.triggered.connect(self.ninepx)



        # Guardar 
        self.pbSave.clicked.connect(self.save)

    def habEscritura(self):
        self.draw = not self.draw
        
        print("draw: ", self.draw)

        color_actual = self.pbDot.palette().button().color().name()

        # nuevo_color = "red" if color_actual != "red" else "blue"

        if color_actual == "white": 
            nuevo_color = "blue"

        else:
            nuevo_color = "white"

        print(nuevo_color)
        nuevo_estilo = self.estilo_original + f"background-color: {nuevo_color};"

        # print(nuevo_estilo)
        # Aplicar el nuevo estilo al botón
        self.pbDot.setStyleSheet(nuevo_estilo)


    def mousePressEvent(self, event):
        # Obtener las coordenadas del clic
        if  self.draw: 
            self.last_point = event.pos()
            self.dibujando = True
            self.update()

    def mouseMoveEvent(self, event):
        # Obtener las coordenadas del movimiento del ratón
        current_point = event.pos()

        if self.dibujando & self.draw: 
            # Crear un QPainter y configurarlo para dibujar en el QPixmap del tablero
            painter = QPainter(self.pixmap_tablero)
            # painter.setPen(QPen(self.pen_color, self.pen_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.setPen(QPen(self.brushColor, self.brushSize, Qt.SolidLine,Qt.RoundCap, Qt.RoundJoin))
            painter.drawLine(self.last_point, current_point)
            painter.end()

            # Actualizar la imagen en el tablero
            self.tablero.setPixmap(self.pixmap_tablero)

            # Forzar la actualización de la interfaz
            self.repaint()

            # Actualizar la última posición
            self.last_point = current_point
            self.update()

    def mouseReleaseEvent(self, event):
        # Al soltar el botón del ratón, dejar de dibujar
        self.dibujando = False
        self.update()
    
    ## Metodo para llamar inicializar camara
    def actualizar_interfaz(self, frame):
        # Convertir el frame de OpenCV a un formato compatible con QImage
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)

        # Mostrar la imagen de la cámara en un QLabel
        self.pixmap = QPixmap.fromImage(q_image)
        
        # Se escribe en el tablero que se encuentra en el fondo. 
        self.tablero_2.setPixmap(self.pixmap)

    def clear(self):
        self.pixmap_tablero.fill(QColor(0, 255, 0,0))
        self.update()
        
        print("limpiando tablero")


    def save(self):
        filePath, _ = QFileDialog.getSaveFileName(self,"Guardar imagen","", "PNG(*.png);;JPEG(*.jpg *.jpeg);; All Files(*.)")
        if filePath == "":
            return
        
        combined_image = QImage(self.pixmap_tablero.size(), QImage.Format_ARGB32)

        combined_image.fill(Qt.transparent)

        # Pintar las dos imágenes en la imagen combinada
        painter = QPainter(combined_image)
        painter.drawPixmap(0, 0, self.pixmap)
        painter.drawPixmap(0, 0, self.pixmap_tablero)
        
        painter.end()
       
        
        combined_image.save(filePath)

    #Pinceles y tamaños 
    
    #Tamaños de pincel
    def onepx(self):
        self.brushSize = 1
    def threepx(self):
        self.brushSize = 3
    def fivepx(self):
        self.brushSize = 5
    def sevenpx(self):
        self.brushSize = 7
    def ninepx(self):
        self.brushSize = 9

    #Colores 
    def brushBlack(self):
        self.brushColor = Qt.black
    def brushRed(self):
        self.brushColor = Qt.red
    def brushBlue(self):
        self.brushColor = Qt.blue
    def brushGreen(self):
        self.brushColor = Qt.green
    def brushYellow(self):
        self.brushColor = Qt.yellow
    def brushWhite(self):
        self.brushColor = Qt.white
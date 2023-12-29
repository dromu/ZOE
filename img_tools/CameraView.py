import sys
import cv2
import numpy as np
from PyQt5.QtCore import Qt, QTimer, QObject, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
import math 
from math import radians, degrees

class ProcesadorCamara(QObject):
    senal_actualizacion = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()

        # Inicializar la cámara de OpenCV
        self.cap = cv2.VideoCapture(0)

        # Iniciar el temporizador para capturar frames periódicamente
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_frame)
        self.timer.start(33)  # Actualizar cada 33 ms (aproximadamente 30 fps)
        
        self.frame = []

    def iniciar_camara(self):
        if not self.cap.isOpened():
            print("Error: No se pudo abrir la cámara.")
        else:
            print("Cámara iniciada.")

    def actualizar_frame(self):
        ret, self.frame = self.cap.read()

        #Acomodado a la resolucion de la Genius 
        ancho   = 1344
        alto    = 756

        self.frame = cv2.resize(self.frame, (ancho, alto))
        self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)

        if ret:
            # Realizar cualquier procesamiento adicional aquí si es necesario
            # Emitir la señal con el frame actualizado
            
            self.senal_actualizacion.emit(self.frame)
    
    def colorComplementary(self):

        # lectura archivo de coordenadas
        with open("img_tools\position.dat", 'r') as archivo:
            coordenadas  = archivo.read()
        # Procesar o imprimir el contenido según sea necesario
        
        coordenadas = eval(coordenadas)
        coordenada1, coordenada2 = coordenadas
        x1, y1 = coordenada1
        x2, y2 = coordenada2

        #Seleccion de region de interes
        imgROI = self.frame[y1:y2, x1:x2]

        #Transformacion al espacio HSV
        R = (imgROI[:,:,0]/255).mean()
        G = (imgROI[:,:,1]/255).mean()
        B = (imgROI[:,:,2]/255).mean()

        print(R, G, B)

        num = 0.5*((R-G) + (R-B))
        den = math.sqrt((R-G)**2 + (R-B)*(G-B))
        H = degrees(np.arccos(num/den))

        H = 360-H

        if H>180:
            H = H-360

        Hcomp = H + 180

        I = 1
        S = 1

        dato = Hcomp

        R_ = 0
        G_ = 0
        B_ = 0

        if  dato < 120: 
            R_ = I*( 1+ ( (S*np.cos(  radians(dato)  ) ) / np.cos( radians(60-dato)  )))
            G_ = 3*I - (R+B)
            B_ = I*(1-S)

        elif dato >= 120 and dato <240:
            R_ = I*(1-S)
            G_ = I * ( 1 + (S* np.cos(radians(dato-120)  )) / ( np.cos(radians(180-dato))  ))
            B_ = 3*I - (R+G)

        elif dato >= 240 and dato <360:
            R_ = 3*I - (B+G)
            G_ = I*(1-S)
            B_ = I*(1 + (  (S * np.cos(radians(dato-240)  ) ) / ( np.cos(radians(300-dato))) ))

        print(dato)

        R_ = R_*255
        G_ = G_*255
        B_ = B_*255

        R_ = min(255, max(0, R_))
        G_ = min(255, max(0, G_))
        B_ = min(255, max(0, B_))

        return R_, G_, B_

        
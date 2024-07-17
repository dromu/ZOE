import sys
import cv2
import numpy as np
from PyQt5.QtCore import Qt, QTimer, QObject, pyqtSignal,QMutex, QMutexLocker
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
import math 
from math import radians, degrees

class ProcesadorCamara(QObject):
    senal_actualizacion = pyqtSignal(np.ndarray)
    senal_conexion_perdida = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.idxCamera = self.readCamera()

        # Inicializar la cámara de OpenCV
        self.cap = cv2.VideoCapture(self.idxCamera)
    
        # Iniciar el temporizador para capturar frames periódicamente
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_frame)
        self.timer.start(33)  # Actualizar cada 33 ms (aproximadamente 30 fps)
        self.conexion_perdida_emitida = False
        self.frame = []

        self.mutex = QMutex() 

    def readCamera(self):
        with open("img_tools\camera.dat", 'r') as archivo:
            contenido = archivo.read()
        
        if contenido[0] == None:
            return 0 
        else: 
            return int(contenido[0])


    def iniciar_camara(self):

        self.idxCamera = self.readCamera()
        
        # Inicializar la cámara de OpenCV
        self.cap = cv2.VideoCapture(self.idxCamera)

        print(self.idxCamera)

        if not self.cap.isOpened():
            print("Error: No se pudo abrir la cámara.")

            self.senal_conexion_perdida.emit()
        else:
            print("Cámara iniciada.")

    def actualizar_frame(self):
        ret, self.frame = self.cap.read()

        #Acomodado a la resolucion de la Genius 
        # FullHD
        # ancho   = 1600
        # alto    = 891

        ancho   = 1200
        alto    = 900


    

        if ret:
            # Realizar cualquier procesamiento adicional aquí si es necesario
            # Emitir la señal con el frame actualizado
            
            self.frame = cv2.resize(self.frame, (ancho, alto))
            self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            self.senal_actualizacion.emit(self.frame)

            if self.conexion_perdida_emitida:
                self.conexion_perdida_emitida = False
        else: 
            self.senal_conexion_perdida.emit()
            if not self.conexion_perdida_emitida:
                self.emitir_conexion_perdida()
                
    def emitir_conexion_perdida(self):
        self.senal_conexion_perdida.emit()
        self.conexion_perdida_emitida = True

    def currentFrame(self):
   
        with QMutexLocker(self.mutex):
            if self.frame is not None:
                return self.frame.copy()
            else:
                return None
        
        
    def colorComplementary(self):

        # lectura archivo de coordenadas
        with open("img_tools\position.dat", 'r') as archivo:
            coordenadas  = archivo.read()
        # Procesar o imprimir el contenido según sea necesario
        
        coordenadas = eval(coordenadas)
        coordenada1, coordenada2 = coordenadas
        x1, y1 = coordenada1
        x2, y2 = coordenada2

        maximo  = self.frame.shape
        maxX    = maximo[1]
        maxY    = maximo[0]

        #minimos
        x1 = 0 if x1 < 0 else x1
        x2 = 0 if x2 < 0 else x2

        y1 = 0 if y1 < 0 else y1
        y2 = 0 if y2 < 0 else y2

        #maximos
        x1 = maxX if x1 > maxX else x1
        x2 = maxX if x2 > maxX else x2

        y1 = maxY if y1 > maxY else y1
        y2 = maxY if y2 > maxY else y2


        if x1 > x2:
            tempX = x2
            x2 = x1
            x1 = tempX

        if y1 > y2:
            tempY = y2
            y2 = y1
            y1 = tempY

        self.imgROI = self.frame[y1:y2, x1:x2,   :]

        #Transformacion al espacio HSV
        R = np.mean(self.imgROI[:,:,0]/255)
        G = np.mean(self.imgROI[:,:,1]/255)
        B = np.mean(self.imgROI[:,:,2]/255)

        num = 0.5*((R-G) + (R-B))
        den = math.sqrt((R-G)**2 + (R-B)*(G-B))
        
        H = round(degrees(np.arccos(num/den)))

        if  B>G:
            H =  360 -H

        # print("Valor inicial de H: ", H)

        if H>=0 and H<=180:
            Hcomp = H + 180
        else:
            Hcomp = H - 180

        if Hcomp == 360:
            Hcomp = 0


        I = 1
        S = 1

        dato = Hcomp

        print(R, G, B)

        if  dato>= 0 and dato < 120: 
            R_ = I*( 1+ ( (S*np.cos( radians(dato)  ) ) / np.cos( radians(60-dato)  )))
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

        print("RGB complementario", "R:", R_,"G:", G_, "B:", B_)

        maxValue = self.maximoValor(R_,G_,B_)

        R_ = (R_/3)*255
        G_ = (G_/3)*255
        B_ = (B_/3)*255


        R_ = round(min(255, max(0, R_)))
        G_ = round(min(255, max(0, G_)))
        B_ = round(min(255, max(0, B_)))

        return R_, G_, B_

    def maximoValor(self, R,G,B):
        dato = [R,G,B]
        return max(dato)

        




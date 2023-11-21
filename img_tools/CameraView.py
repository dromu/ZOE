import sys
import cv2
import numpy as np
from PyQt5.QtCore import Qt, QTimer, QObject, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

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
        ancho   = 1350
        alto    = 850

        self.frame = cv2.resize(self.frame, (ancho, alto))
        self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)

        if ret:
            # Realizar cualquier procesamiento adicional aquí si es necesario
            # Emitir la señal con el frame actualizado
            
            self.senal_actualizacion.emit(self.frame)
    
    def colorComplementary(self):

        # lectura archivo de coordenadas
        with open("img_tools\position.dat", 'r') as archivo:
            contenido = archivo.read()
        # Procesar o imprimir el contenido según sea necesario
        print(contenido)

        #Aqui se calcula el color complementario y devuelve la longitud de onda

        

       

            
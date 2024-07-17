import sys
from PyQt5 import uic, QtWidgets
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QPoint
from img_tools.CameraView import ProcesadorCamara
from img_tools.cameraSelection import DialogoSeleccionCamara

from PyQt5.QtWidgets import QFileDialog, QActionGroup,QAction,QButtonGroup
import numpy as np 
import os
import cv2 
from PyQt5.QtWidgets import QApplication, QDialog,QMessageBox,QToolTip
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSlider, QLabel
from PyQt5.QtMultimedia import QCameraInfo
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QComboBox, QPushButton, QColorDialog

from img_tools.DrawingBoard import DrawingBoard

from utils.dataPaciente import dataPaciente
from utils.About import aboutZOE
from utils.instruccion import instrucciones
from utils.calibration import calibration
from PyQt5.QtCore import QTimer

from comunication.testConexion import ESP32Client

from PyQt5.QtGui import QCursor
import pydicom
import pickle
import time 

class MyApp(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ui_file = "gui\zoe_main.ui"
        Ui_MainWindow, QtBaseClass = uic.loadUiType(ui_file)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


        #Botones 
        self.ui.tablero = DrawingBoard(self.ui.tablero)                 # Objeto
        self.ui.pbDot.clicked.connect(self.ui.tablero.habEscritura)     # Dibujo libre
        self.ui.pbRect.clicked.connect(self.ui.tablero.habRect)         # Rectangulos 
        self.ui.pbHide.clicked.connect(self.ui.tablero.hideWind)        # Ocultar cambios
        self.ui.pbTrash.clicked.connect(self.ui.tablero.clear)          # Limpiar pantalla
        self.ui.pbElip.clicked.connect(self.ui.tablero.habElipse)       # Boton de generar elipses
        self.ui.pbText.clicked.connect(self.ui.tablero.habText)         # Texto
        self.ui.pbDel.clicked.connect(self.ui.tablero.habDel)           # Eliminacion de escrito
        self.ui.pbROI.clicked.connect(self.ui.tablero.habColor)         # Generacion de color complementario
        self.ui.checkPacient.clicked.connect(self.datosPacientes)
        self.ui.pbExit.clicked.connect(self.exitSystem)
        self.ui.pbDot.clicked.connect(self.habEscritura)
        self.ui.pbROI.clicked.connect(self.habColor)

        self.ui.pbOpen.clicked.connect(self.openTray)


        self.buttons = ["pbDot", "pbRect", "pbElip", "pbText","pbDel","pbROI","pbHide"]
        self.botones = []
        self.funcionHab = { self.ui.pbDot:  self.ui.tablero.habEscritura, 
                            self.ui.pbRect: self.ui.tablero.habRect,
                            self.ui.pbElip: self.ui.tablero.habElipse,
                            self.ui.pbText: self.ui.tablero.habText,      
                            self.ui.pbDel:  self.ui.tablero.habDel,     
                            self.ui.pbROI:  self.ui.tablero.habColor,
                            self.ui.pbHide: self.ui.tablero.hideWind
                            }

       
        for i, button in enumerate(self.buttons): 
            base        =  self.ui
            buttonDato  =  getattr(base, button)
            buttonDato.clicked.connect(lambda _, idx=i: self.cambiarColor(idx))
            self.botones.append(buttonDato)
            

        #   Eje X 
        self.valueX = 0
        self.ui.plusX.clicked.connect(self.aumentarX)
        self.ui.minusX.clicked.connect(self.disminuirX)

        #   Eje Y
        self.valueY = 0
        self.ui.plusY.clicked.connect(self.aumentarY)
        self.ui.minusY.clicked.connect(self.disminuirY)        

        #   Eje Y
        self.valueZ = 0
        self.ui.plusZ.clicked.connect(self.aumentarZ)
        self.ui.minusZ.clicked.connect(self.disminuirZ)  

        self.ui.pbCamera.clicked.connect(self.cameraSelection)
        self.ui.pbColor.clicked.connect(self.paletteColor) 
        self.ui.tamPincel.currentIndexChanged.connect(self.sizePincel)
        self.ui.tamPincel.setCurrentIndex(1) #Defecto 3px
        self.ui.pbCalibrate.setEnabled(False)  
        
        self.nombre         = ""
        self.sexo           = ""
        self.typeid         = ""
        self.identificacion = ""
        self.edad           = ""
        self.birthday       = ""
        self.date           = ""
        self.posPaciente    = ""
        self.modalidad      = ""
        self.imgType        = ""
        self.institucion    = ""
        self.nameEquipo     = ""
        self.descrImg       = ""
        self.respuestaCon = []
        self.cerrado = False
        self.movAumento = 5

        # Valores iniciales de las variables
        self.flagEscritura = False
        self.flagColor = False
        self.visCamera = False
        self.flagConx = False

        self.actualButton = []

        self.previusButton = "nan"
        self.datoAuto  = None

        # Imagen de inicio de en lugar de visualizacion de muestras 
        self.img_pixmap = QPixmap("images\micros.png")
        self.ui.cameraSpace.setPixmap(self.img_pixmap)

        self.client = ESP32Client('192.168.4.1', 80)
        self.stateConexion = False

        # Boton de inicio de conexion
        self.ui.pbConnect.clicked.connect(self.connectESP)
        self.original_style = self.ui.pbConnect.styleSheet()

        self.ui.procesador_camara = ProcesadorCamara()
        
        self.R_ = 0
        self.G_ = 0
        self.B_ = 0

        
   
        #Boton de guardar pantallas 
        self.ui.pbSave.clicked.connect(self.save)

        ## Elementos en el main 
        #Texto inicial de conexion 
        self.ui.txtConnect.setText("No conectado")
        self.ui.txtConnect.setAlignment(Qt.AlignRight)
        # Slider de espectro visible
        self.ui.VisibleEsp.valueChanged.connect(self.slider_value_changed)

        self.ui.brilloSlider.valueChanged.connect(self.sliderBrillo)
        
        # Deshabilitamos los elementos del main, estos se irán actualizando
        self.ui.wavelength.setEnabled(False)
        self.ui.VisibleEsp.setEnabled(False)
        self.ui.RB_manual.setEnabled(False)
        self.ui.RB_auto.setEnabled(False)
        self.ui.RB_white.setEnabled(False)
        self.ui.actionCalibrar.setEnabled(False)

        self.ui.aumentoGroup.setEnabled(False)
        self.autoAnte = None

        # Cambiar el valor del slider en texto
        self.ui.wavelength.returnPressed.connect(self.line_edit_return_pressed)

        # Seleccion de modo luz blanca por defecto
        self.ui.RB_white.setChecked(True)

        # Conectar todos los botones de radio a la función processRadioButton
        buttons = [self.ui.RB_manual, self.ui.RB_auto, self.ui.RB_white]
        for button in buttons:
            button.toggled.connect(lambda state, b=button: self.processRadioButton(b, self.ui.VisibleEsp, self.ui.wavelength))

        self.ui.value = 380

        self.previusNamebutton = None
        self.manejoButton(False)

        self.valueMotor = ""
        self.ui.pbAbout.clicked.connect(self.aboutZOE)
        self.ui.pbCalibrate.clicked.connect(self.calibrarZOE)
        self.ui.pbHelp.clicked.connect(self.instruccionesZOE)

        self.rbuttonAug = 4
        
        QToolTip.setFont(QToolTip.font())
        self.ui.pbDot.setToolTip('Lápiz')
        self.ui.pbCalibrate.setToolTip("Calibrar")
        self.ui.pbElip.setToolTip("Circulo")
        self.ui.pbText.setToolTip("Texto")
        self.ui.pbTrash.setToolTip("Limpiar")
        self.ui.pbDel.setToolTip("Borrador")
        self.ui.checkPacient.setToolTip("Información del paciente")
        self.ui.pbROI.setToolTip("Color complementario")
        self.ui.pbHide.setToolTip("Ocultar")
        
        self.ui.pbAbout.setToolTip("Acerca de")
        self.ui.pbHelp.setToolTip("Ayuda")
        self.ui.pbRect.setToolTip("Rectángulo")
        self.ui.tamPincel.setToolTip("Tamaño")
        self.ui.pbCamera.setToolTip('Cámara')
        self.ui.pbColor.setToolTip("Color")
        self.ui.pbSave.setToolTip("Guardar")
        self.ui.pbConnect.setToolTip("Conexión")
        self.ui.pbExit.setToolTip("Salir")

        self.ui.RB_white.setToolTip("Luz blanca")
        self.ui.RB_auto.setToolTip("Automático")
        self.ui.RB_auto.setToolTip("Manual")

        self.flagCamara = True
        # self.flagDesCam = True

        ############### Listas de elementos #####################

        self.ui.aumentoMov.currentIndexChanged.connect(self.aumentoRev)
        self.ui.aumentoMov.setCurrentIndex(2)
        
        # self.ui.aumentoGroup.currentIndexChanged.connect(self.aumentoImg)
        self.ui.aumentoGroup.setCurrentIndex(0)

        # self.ui.muestraNum.currentIndexChanged.connect(self.eleccionMuestra)

        self.velXY = 500
        self.velZ = 100

        self.ui.velXY.currentIndexChanged.connect(self.velocXY)
        self.ui.velXY.setCurrentIndex(3)

        self.ui.velZ.currentIndexChanged.connect(self.velocZ)
        self.ui.velZ.setCurrentIndex(2)
      
        self.Zmax = {"4x": 10, "10x":5, "40x": 1.5}

        ###############################################################
       
        self.brilloColor = "150"
        
        self.ui.procesador_camara.senal_conexion_perdida.connect(self.mostrar_mensaje_conexion_perdida)

        self.limitPosition = { "muestra1": [ ] ,
                               "muestra1": [] ,
                               "muestra1": [] ,
                               "muestra1": [] } 
        
        self.stateOpen = False

        self.stateAum = "4X"
        self.stateMuestra = []

        self.FitXY  = 100
        self.FitZ   = 100
        self.pasoXY = 1
        self.pasoZ  = 1

        self.ui.pbGo.clicked.connect(self.goStation)
        self.ui.pbFocus.clicked.connect(self.autofocus)


        # Limites de la muestras X1 Y1 X2 Y2 
        self.limitM1 = [ 70, 30, 30, 60 ]
        self.limitM2 = [ 40, 70, 70, 90 ]
        self.limitM3 = [ 40, 70, 70, 90 ]
        self.limitM4 = [ 40, 70, 70, 90 ]



    def laplaceAutofocus(self, image): 
        # Verificar si la imagen se cargó correctamente
        if image is None:
            raise ValueError(f"Could not load image from {image}")
        
        # Aplicar el filtro Laplaciano a la imagen
        laplacian = cv2.Laplacian(image, cv2.CV_64F)
        
        # Calcular la varianza del laplaciano
        laplacian_var = laplacian.var()
        
        # Determinar si la imagen está borrosa comparando con el umbral
        
        
        return round(laplacian_var, 0)
    
    
    def autofocus(self):

        regFocus    = []
        zpaso       = 1
        vel         = 500
        minZ        = 0
        maxZ        = 10
        varAutofocus= {}
        mov         = 10

        #Leer en que aumento se encuentra 
        if self.stateAum == "4X": 
            zpaso       = 1
            maxZ        = 10
            minZ        = 5
        elif self.stateAum == "10X": 
            zpaso       = 0.1
            maxZ        = 6
            minZ        = 2
        elif self.stateAum == "40X": 
            zpaso       = 0.01
            maxZ        = 3
            minZ        = 1

        while(maxZ >= minZ):

            maxZ -= zpaso
            maxZ = round(maxZ,3)

            pos = "G00 Z" + str(maxZ) + " F500"
            print(maxZ)
            self.sendHardware(pos)
            
            img = self.ui.procesador_camara.currentFrame()

            varImg = self.laplaceAutofocus(img)
            varAutofocus[str(pos)] = varImg
        
        enfPos = max(varAutofocus, key=varAutofocus.get)

        self.sendHardware(enfPos)
            

    def updateDatamov(self):

        print(f'Valor FitXY {self.FitXY}')

        velocidad   = (1,10,100,500,2500)
        paso        = (5,2,1,0.5,0.1,0.01,0.005,0.001)

        self.ui.velXY.setCurrentIndex(velocidad.index(self.FitXY))
        self.ui.velZ.setCurrentIndex(velocidad.index(self.FitZ))

        self.ui.aumentoMov.setCurrentIndex(paso.index(self.pasoXY))
        self.ui.aumentoMovZ.setCurrentIndex(paso.index(self.pasoZ))
        
    def goStation(self):

        # Lectura del espacio elegido 
        muestra             = ("muestra1", "muestra2", "muestra3", "muestra4")
        indM                = self.ui.muestraNum.currentIndex()
        print(f'muestra: {muestra[indM-1]}')

        self.stateMuestra   = muestra[indM-1]

        # Lectura del objetivo elegido
        objetivo        = ("4X","10X","40X")
        indOb           = self.ui.aumentoGroup.currentIndex()
        self.stateAum   = objetivo[indOb]
        
        # Movimiento Revolver 
        self.settingObj()
        self.settingMuest()
        

    def settingObj(self):  
        
        # Baja la posicion para no pegar con los objetivos 
        self.valueZ = 10
        codeText        = "G00 Z"+ str(self.valueZ) + " F2500" 
        self.sendHardware(codeText)
        self.coordCurrent()
        
        
        #Movimiento del objetivo 
        if self.stateAum == "4X":
            self.valueZ =   10
            self.FitXY  =   500
            self.FitZ   =   500
            self.pasoXY =   2
            self.pasoZ  =   1

            self.sendHardware("2")
            self.updateDatamov()

        elif self.stateAum == "10X":
            self.valueZ = 5
            self.FitXY  =   500
            self.FitZ   =   100
            self.pasoXY =   0.5
            self.pasoZ  =   0.5

            self.sendHardware("1")
            self.updateDatamov()

        elif self.stateAum == "40X":
            self.valueZ = 2
            self.FitXY  =   100
            self.FitZ   =   10
            self.pasoXY =   0.1
            self.pasoZ  =   0.01

            self.sendHardware("R")
            self.updateDatamov()

    def settingMuest(self):

        if self.stateMuestra == "muestra1":

            self.valueX, self.valueY = (55, 40)

            pos = "G00 Z10 F2500"
            self.sendHardware(pos)

            pos = "G00 X" + str(self.valueX)  +" Y" + str(self.valueY) + " F2500"
            self.sendHardware(pos)

            pos = "G00 Z" +  str(self.valueZ) + " F1000"
            self.sendHardware(pos)

            self.limits = self.limitM1
            
            self.coordCurrent()

        elif self.stateMuestra == "muestra2":
            self.valueX, self.valueY = (55, 70)

            pos = "G00 Z10 F2500"
            self.sendHardware(pos)

            pos = "G00 X" + str(self.valueX)  +" Y" + str(self.valueY) + " F2500"
            self.sendHardware(pos)

            pos = "G00 Z" +  str(self.valueZ) + " F1000"
            self.sendHardware(pos)

            self.limits = self.limitM2
            
            self.coordCurrent()

        elif self.stateMuestra == "muestra3":
            self.valueX, self.valueY = (165, 40)

            pos = "G00 Z10 F2500"
            self.sendHardware(pos)

            pos = "G00 X" + str(self.valueX)  +" Y" + str(self.valueY) + " F2500"
            self.sendHardware(pos)

            pos = "G00 Z" +  str(self.valueZ) + " F1000"
            self.sendHardware(pos)

            self.limits = self.limitM3
            
            self.coordCurrent()

        elif self.stateMuestra == "muestra4":
            self.valueX, self.valueY = (55, 70)

            pos = "G00 Z10 F2500"
            self.sendHardware(pos)

            pos = "G00 X" + str(self.valueX)  +" Y" + str(self.valueY) + " F2500"
            self.sendHardware(pos)

            pos = "G00 Z" +  str(self.valueZ) + " F1000"
            self.sendHardware(pos)
            
            self.limits = self.limitM4

            self.coordCurrent()


    def coordCurrent(self):
        self.ui.coordZ.setText("{:.3f}".format(self.valueZ))
        self.ui.coordX.setText("{:.3f}".format(self.valueX))
        self.ui.coordY.setText("{:.3f}".format(self.valueY))

    def openTray(self): 
        
        if self.stateOpen:
            #Envia los valores de la posicion 
            self.valueZ = 5
  
            #Sube bandeja
            codeMov = "G00 Z" + str(self.valueZ) + " F1500"
            self.sendHardware(codeMov)

            # ACtualizacion de la posicion 
            self.coordCurrent()
            self.stateOpen = not self.stateOpen

        else: 
            # Bajar las bandejas 
            self.valueZ = 30
            codeMov = "G00 Z" + str(self.valueZ) + " F2000"
            self.sendHardware(codeMov)

            #Cambia estado y actualiza coordenada.
            self.stateOpen = not self.stateOpen
            self.coordCurrent()

        
    def sliderBrillo(self,value):
        self.brilloColor = str(value).zfill(3)

        if self.ui.RB_white.isChecked():
            text = ("W000000000" + str(self.brilloColor))
            
        elif self.ui.RB_manual.isChecked():
            text = ("M" + str(self.ui.value) +  "000000" + str(self.brilloColor))

        elif self.ui.RB_auto.isChecked():            
            text = ("A" + str(self.datoAuto) + str(self.brilloColor))

        self.sendHardware(text)

    def show_message_box(self, title , message, icon=QMessageBox.Information, buttons=QMessageBox.Ok):

        self.visCamera = True
        msg_box = QMessageBox()
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(buttons)
        msg_box.exec_()
    
    def mostrar_mensaje_conexion_perdida(self):
        if self.ui.procesador_camara.conexion_perdida_emitida and self.flagCamara:
            
            QMessageBox.warning(self, "Error", "Se ha perdido la conexión con la cámara.")
            time.sleep(1)
            self.ui.pbConnect.click()
            self.flagCamara = False

    def closeEvent(self, event):
        self.ui.procesador_camara.cap.release()
        event.accept()

    def cameraSelection(self):
        cameraSel = DialogoSeleccionCamara()
        cameraSel.exec_()

    def sizePincel(self):
        size = (1,3,5,7,9)
        ind= self.ui.tamPincel.currentIndex()

        self.ui.tablero.pincelSize(size[ind])

    def paletteColor(self):
        color = QColorDialog.getColor()
        if color.isValid():
            # Aquí podrías hacer algo con el color seleccionado
            print("Color seleccionado:", color.name())
            color_hex = color.name()

            # self.ui.pbColor.setStyleSheet(f"background-color: {color_hex};")
            self.ui.tablero.pincelColor(color_hex)

    def aumentoImg(self):
        size = (4,10,40)
        ind= self.ui.aumentoGroup.currentIndex()
        self.rbuttonAug = size[ind]

        if size[ind] == 4:

            pos = "%G00 Z20 F2500%"
            text = "%2%"
            if self.client.send_receive(pos) == "OK":
                pos = "%G28 Z %"
                self.client.send_receive(text)
               
                

        elif size[ind] == 10:
            text = "%1%"
            pos = "%G00 Z20 F2500%"
            if self.client.send_receive(pos) == "OK":
                pos = "%G28 Z %"
                self.client.send_receive(text)
                
                

        elif size[ind] == 40:
            text = "%R%"
            pos = "%G00 Z20 F2500%"
            if self.client.send_receive(pos) == "OK":
                pos = "%G28 Z %"
                self.client.send_receive(text)
                

        

    def velocXY(self):
        size = (1,10,100,500,2500)
        ind= self.ui.velXY.currentIndex()        
        self.velXY = size[ind]

    def velocZ(self):
        size = (1,10,100,500,2500)
        ind= self.ui.velZ.currentIndex()        
        self.velZ = size[ind]


    def aumentarX(self):
        self.valueX = self.valueX  + self.movAumento

        if self.valueX >= self.limits[0]:
            self.valueX = self.limits[0]

        self.valueX = round(self.valueX,3)
        # self.valueX= self.limitValue(self.valueX)
        self.ui.coordX.setText("{:.3f}".format(self.valueX))

        pos = "%G00 X" + str(self.valueX) + " F"+ str(self.velXY) + "%"
        if self.client.send_receive(pos) != "OK":
            print("Error")

    def disminuirX(self):
        self.valueX = self.valueX - self.movAumento

        if self.valueX <= self.limits[2]:
            self.valueX = self.limits[2]

        self.valueX = round(self.valueX,3)
        # self.valueX = self.limitValue(self.valueX)
        self.ui.coordX.setText("{:.3f}".format(self.valueX)) # Muestra siempre con tres cifras decimales
        
        pos = "%G00 X" + str(self.valueX) + " F"+ str(self.velXY) + "%"
        if self.client.send_receive(pos) != "OK":
            print("Error")

    def aumentarY(self):
        self.valueY = self.valueY  + self.movAumento

        if self.valueY >= self.limits[3]:
            self.valueY = self.limits[3]


        self.valueY = round(self.valueY,3)
        # self.valueY= self.limitValue(self.valueY)
        self.ui.coordY.setText("{:.3f}".format(self.valueY))

        pos = "%G00 Y" + str(self.valueY) + " F"+ str(self.velXY) + "%"
        if self.client.send_receive(pos) != "OK":
            print("Error")

    def disminuirY(self):
        self.valueY -= self.movAumento

        if self.valueY <= self.limits[1]:
            self.valueY = self.limits[1]

        if self.valueY<=0: 
            self.valueY = 0

        self.valueY = round(self.valueY,3)
        # self.valueY= self.limitValue(self.valueY)
        self.ui.coordY.setText("{:.3f}".format(self.valueY))

        pos = "%G00 Y" + str(self.valueY) + " F"+ str(self.velXY) + "%"
        if self.client.send_receive(pos) != "OK":
            print("Error")

    def aumentarZ(self):
        self.valueZ = self.valueZ  +  self.movAumento
        self.valueZ = round(self.valueZ,3)
        # self.valueZ= self.limitValue(self.valueZ)
        self.ui.coordZ.setText("{:.3f}".format(self.valueZ))
        pos = "%G00 Z" + str(self.valueZ) + " F"+ str(self.velZ) + "%"
        if self.client.send_receive(pos) != "OK":
            print("Error")

    def disminuirZ(self):
        self.valueZ -=  self.movAumento

        if self.valueZ<=0: 
            self.valueZ = 0

        self.valueZ = round(self.valueZ,3)
        # self.valueZ= self.limitValue(self.valueZ)
        self.ui.coordZ.setText("{:.3f}".format(self.valueZ))
        pos = "%G00 Z" + str(self.valueZ) + " F"+ str(self.velZ) + "%"
        if self.client.send_receive(pos) != "OK":
            print("Error")
    
    
    def aumentoRev(self,indice):  
        valueSpinbox = [5,2,1, 0.5, 0.1,0.01,0.005, 0.001]
        self.movAumento = valueSpinbox[indice]

    def instruccionesZOE(self):
        ZOEinstruccion = instrucciones()
        ZOEinstruccion.exec_()


    def aboutZOE(self):
        ZOEabout = aboutZOE()
        ZOEabout.exec_()

    def calibrarZOE(self):

        respuesta = QMessageBox.question(self, 'Calibracion', '¿Desea calibrar el sistema ZOE?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        print(QMessageBox.Yes)

        if respuesta == QMessageBox.Yes:
            self.sendHardware("K000000000")            
            time.sleep(5)
            QMessageBox.information(None, 'Calibración', 'Sistema Calibrado.')


    def readCamera(self):
        with open("img_tools\camera.dat", 'r') as archivo:
            contenido = archivo.read()
        
        if contenido[0] == None:
            salida =  0 
        else: 
            salida =  int(contenido[0])
        
        print(salida)
        return salida 
    
    def exitSystem(self):
        respuesta = QMessageBox.question(self, 'Salir', '¿Estás seguro de que quieres salir?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if respuesta == QMessageBox.Yes:    
            QApplication.quit()
        
    
    def datosPacientes(self,state):
        cuadroDatapac = dataPaciente()
        result = cuadroDatapac.exec_()

        if result == QDialog.Accepted:
            
            # PACIENTE
            self.nombre = cuadroDatapac.namePac.text()
            self.sexo = cuadroDatapac.sexPac.currentText()
            self.typeid = cuadroDatapac.typedocPac.currentText()
            self.identificacion = cuadroDatapac.idPac.text()
            self.edad = cuadroDatapac.agePac.text()  
            self.birthday = cuadroDatapac.birthdatePac.date().toString("dd/MM/yyyy")
            
            #IMAGEN 
            self.date           = cuadroDatapac.dateImg.date().toString("dd/MM/yyyy")
            self.posPaciente    = cuadroDatapac.positionMuestra.currentText()
            self.modalidad      = cuadroDatapac.modImg.text()
            self.imgType        = cuadroDatapac.typeImg.text()
            self.descrImg       = cuadroDatapac.descrImg.text()

            #EQUIPO
            self.institucion    = cuadroDatapac.insEqu.text()
            self.nameEquipo    = cuadroDatapac.nameEqu.text()

            if self.posPaciente == "Si":
                self.posPaciente = [str(int(self.valueX*1000)), str(int(self.valueY*1000)),str(int(self.valueZ*1000))]

            else:
                self.posPaciente = ""
                
        else: 
            self.nombre         = ""
            self.sexo           = ""
            self.typeid         = ""
            self.identificacion = ""
            self.edad           = ""
            self.birthday       = ""
            self.date           = ""
            self.posPaciente    = ""
            self.modalidad      = ""
            self.imgType        = ""
            self.institucion    = ""
            self.nameEquipo     = ""
            self.descrImg       = ""

    def cambiarColor(self, idx): 
        
        for i, boton in enumerate(self.botones):
            if i == idx:

                if self.previusButton == idx:               #Sirve para desactivar el mismo boton presionado
                    boton.setStyleSheet("")
                    self.previusButton = None
                    self.previusNamebutton = None
                    
                else:

                    if self.previusNamebutton != None:
                        self.funcionHab[self.previusNamebutton]()

                    # Cambiar el color del botón presionado
                    boton.setStyleSheet("background-color: green")

                    self.previusButton = idx
                    self.previusNamebutton = boton
                    self.actualButton = boton

            else:
                # Restaurar el color original de los demás botones
                boton.setStyleSheet("")
                



    def manejoButton(self, condicion): 
        buttonName = ("pbDot","pbRect","pbHide","pbTrash", "pbElip", "pbText", "pbDel", "pbROI", "pbSave", "pbArrow", "pbBack", "pbForw","checkPacient",
                      "aum4x","aum10x","aum40x","aum100x", "aumentoMov","coordX","coordY", "coordZ", "plusX","plusY", "plusZ", "minusX", "minusY", "minusZ",
                      "RB_auto", "RB_manual", "RB_white", "VisibleEsp", "wavelength", "aumentoGroup", "muestraNum")

        if condicion:
            for key in buttonName:
                button = getattr(self.ui, key, None)
                if button:
                    button.setEnabled(condicion)

        else:
            for key in buttonName:
                button = getattr(self.ui, key, None)
                if button:
                    button.setEnabled(condicion)
    

        

    def habEscritura(self):
        self.flagEscritura = not self.flagEscritura

        # color = "red" if self.flagEscritura else "white"
        # self.ui.pbDot.setStyleSheet(f"QPushButton {{ background-color: {color}; }}")

    
    def habColor(self):
        #entra con el segundo click
        self.flagColor = not self.flagColor

        if self.flagColor == False:
            self.ui.RB_auto.setChecked(True)
            self.ui.RB_auto.setEnabled(True)
            
            # Al presionar dos veces se comprueba el color complementario 
            self.R_,self.G_,self.B_ = self.ui.procesador_camara.colorComplementary()

            self.datoAuto  = str(self.R_).zfill(3)  +  str(self.G_).zfill(3)  +  str(self.B_).zfill(3)
            
            if self.datoAuto != None:
                    self.sendHardware("A"+self.datoAuto + self.brilloColor)
                    
                    print("A"+self.datoAuto + self.brilloColor)
                   

    def actualizar_interfaz(self, frame):
        if self.visCamera:
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            self.ui.pixmap = QPixmap.fromImage(q_image)
            self.ui.cameraSpace.setPixmap(self.ui.pixmap)
        
        else: 
            #Coloca una imagen sino no actualiza
            self.ui.cameraSpace.setPixmap(self.img_pixmap)

    

    def save(self):
        combined_image = QImage(self.ui.tablero.size(), QImage.Format_ARGB32)
        combined_image.fill(Qt.transparent)
        painter = QPainter(combined_image)
        painter.drawPixmap(0, 0, self.ui.pixmap)
        painter.drawPixmap(0, 0, self.ui.tablero.pixmap_tablero)
        painter.end()

        # Convierte QImage a arreglo NumPy
        width = combined_image.width()
        height = combined_image.height()
        ptr = combined_image.bits()
        ptr.setsize(combined_image.byteCount())
        arr = np.array(ptr).reshape((height, width, 4))
        arr = cv2.cvtColor(arr, cv2.COLOR_BGR2RGB)
        imagen_numpy = arr[:, :, :3]
       

        filePath, extension = QFileDialog.getSaveFileName(self, "Guardar imagen", "", "DICOM (*.dcm);;PNG (*.png);;JPEG (*.jpg *.jpeg);;All Files (*)")

       
        if filePath == "":
            return
        
        print("filePath: ", filePath)
        print("extension", extension )

        if filePath:
            _, file_extension = os.path.splitext(filePath)
            print("Archivo seleccionado:", filePath)
            print("Extensión seleccionada:", file_extension)
        
        if file_extension == ".dcm":
            # Crear un objeto DICOM
            dataset = pydicom.Dataset()


            # Agregar información de metadatos
            
            dataset.StudyDescription = self.descrImg

            dataset.PatientName         = self.nombre
            dataset.PatientID           = self.typeid + "  "+self.identificacion
            dataset.PatientBirthDate    = self.birthday 
            dataset.PatientSex          = self.sexo
            dataset.PatientAge          = self.edad

            dataset.StudyDate           = self.date
            dataset.ImagePositionPatient = self.posPaciente
            dataset.Modality            = self.modalidad
            dataset.ImageType           = self.imgType

            dataset.InstitucionName     = self.institucion
            dataset.Manufacturer        = self.nameEquipo
                    
            color_channels = 3
            # Asignar la imagen y sus metadatos al objeto DICOM
            dataset.PixelData = imagen_numpy.tobytes()
            dataset.Rows, dataset.Columns= imagen_numpy.shape[:2]
            dataset.PlanarConfiguration = 0  # RGB intercalado
            dataset.PixelSpacing = [1.0, 1.0]
            dataset.BitsAllocated = 8
            dataset.BitsStored = 8
            dataset.SamplesPerPixel = color_channels
            dataset.PhotometricInterpretation = "RGB"
            dataset.HighBit = 7
            dataset.PixelRepresentation = 0
            dataset.RescaleIntercept = 0
            dataset.RescaleSlope = 1

            # Configuración adicional necesaria para evitar el error
            dataset.is_little_endian = True  # Puedes ajustar según tus necesidades
            dataset.is_implicit_VR = True  # Puedes ajustar según tus necesidades

            # Guardar el objeto DICOM en un archivo
            ruta_salida_dicom = filePath
            dataset.save_as(ruta_salida_dicom)
        else:       
            combined_image.save(filePath)

    def processRadioButton(self, radio_button, slider, wavelength):
        if radio_button.isChecked():

            print(radio_button.text())
            
            if radio_button.text() == 'M':
                # Se habilitan todas las modificaciones al espectro 
                slider.setEnabled(True)    
                wavelength.setEnabled(True)    

                # Envio en modo manual

                text = ("M" + str(self.ui.value) +  "000000" + str(self.brilloColor))
                self.sendHardware(text )
                
            if radio_button.text() == 'A':
           
                if self.datoAuto != None:
                    text = ("A"+self.datoAuto + str(self.brilloColor))

                    self.sendHardware(text )
                    
                    print(text)


            if radio_button.text() == 'W':
                # Se limitan y paran todas las acciones 

                text = "W000000000" + str(self.brilloColor) 
                 
                self.sendHardware(text)
                self.ui.wavelength.setEnabled(False)
                self.ui.VisibleEsp.setEnabled(False)
                
            slider.setValue(self.ui.value)
           
    # Recibe los valores de cambio del slider
    def slider_value_changed(self, value):
        # Checkea el boton manual
        if self.ui.RB_manual.isChecked():
            self.ui.wavelength.setText(str(value))
            self.ui.value = int(value) # ACtualizamos el valor para que la barra quede en el mismo punto del manual
            
            
            # Envio en modo manual
            
            text = ("M" + str(value) +  "000000" + str(self.brilloColor) )
            self.sendHardware(text )
            
        else:
            # Se deshabilita cualquier accion diferente
            self.ui.wavelength.setEnabled(False)
            self.ui.VisibleEsp.setEnabled(False)


    # Hace referencia al recuadro para cambio de longitud
    def line_edit_return_pressed(self):
        value = self.ui.wavelength.text()
        if value.isdigit():
            value = int(self.ui.wavelength.text())
            if 380 <= value <= 780:
                self.ui.VisibleEsp.setValue(value)
            else:
                self.ui.wavelength.setText("Invalid value!")
        else:
                self.ui.wavelength.setText("Invalid value!")


    def connectESP(self):
        if not self.stateConexion:

            self.stateConexion = True

            # Cambia color del boton 
            self.ui.pbConnect.setText('C')
            self.ui.pbConnect.setStyleSheet(""" background-color: rgb(50, 255, 50); """ )
            self.ui.txtConnect.setText("Conexión establecida")

            # Encendemos los botonoes 
            self.manejoButton(True)

            self.ui.procesador_camara.iniciar_camara()
            self.ui.procesador_camara.senal_actualizacion.connect(self.actualizar_interfaz)
            self.visCamera = True

            #Se encienden todos los botones 
            self.client.connect() 
        
            #Enciende la luz blanca 
            
            self.client.send_receive("%W000000000255%")

            # Va a home el revolver             
            self.client.send_receive("%2%")

            #Envia Home 
            self.client.send_receive("%G28 X Y Z%")

            #Estable siempre el enable de los motores 
            self.client.send_receive("%M17%")
            self.client.send_receive("%M84 S36000%")
            self.coordCurrent()
        else:
            #Apaga la luz
            self.client.send_receive("%W000000000000%")
            
            # Desahabilita los motores
            self.client.send_receive("%M84%")

            time.sleep(1)

            #Se apagan todos los botones 
            self.client.disconnect()
            self.stateConexion = False
            self.manejoButton(False)
            self.visCamera = False
            self.ui.pbConnect.setStyleSheet(self.original_style)
            

    def guardar_variable(self,variable,archivo):
        with open(archivo, 'w') as archivo:
            archivo.write(variable)

    def sendHardware(self, dato):
        print(dato)
        dato = "%"+dato+"%"

        print(dato)
        self.client.send_receive(dato)

        if self.respuestaCon == "error": 
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("No es posible enviar datos. Revisa la conexión")
            msg.setWindowTitle("Conexión")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

            self.ui.pbConnect.setStyleSheet(""" background-color: rgb(255,255,0); """ )
            self.ui.txtConnect.setText("Error de conexión")
            
            
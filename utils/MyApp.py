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
from comunication.TCP_comunication import TCP_comunication
from comunication.wificonnector import WifiConnector
from utils.dataPaciente import dataPaciente
from utils.About import aboutZOE
from utils.instruccion import instrucciones
from utils.calibration import calibration
from PyQt5.QtCore import QTimer

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


        #Color complementario 
        # self.ui.colorComp = complementaryColor(self.ui.tablero)



        #Crea un objeto y llamada un metodo de la clase DrawingBoard

        #Botones de dibujo
        self.ui.tablero = DrawingBoard(self.ui.tablero)                 # Objeto
        self.ui.pbDot.clicked.connect(self.ui.tablero.habEscritura)     # Dibujo libre
        self.ui.pbRect.clicked.connect(self.ui.tablero.habRect)         # Rectangulos 
        self.ui.pbHide.clicked.connect(self.ui.tablero.hideWind)        # Ocultar cambios
        self.ui.pbTrash.clicked.connect(self.ui.tablero.clear)          # Limpiar pantalla
        self.ui.pbElip.clicked.connect(self.ui.tablero.habElipse)       # Boton de generar elipses
        self.ui.pbText.clicked.connect(self.ui.tablero.habText)         # Texto
        self.ui.pbDel.clicked.connect(self.ui.tablero.habDel)           # Eliminacion de escrito
        self.ui.pbROI.clicked.connect(self.ui.tablero.habColor)         # Generacion de color complementario

        # self.ui.barraInfo.textChanged.connect(self.actualizarTexto)
        # self.ui.pbArrow.clicked.connect(self.ui.tablero.habArrow)

        # self.ui.checkPaciente.stateChanged.connect(self.datosPacientes)
        self.ui.checkPacient.clicked.connect(self.datosPacientes)


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
            

        self.ui.pbExit.clicked.connect(self.exitSystem)

        # Union a metodos locales de la clase para cambio de color 
        self.ui.pbDot.clicked.connect(self.habEscritura)
        self.ui.pbROI.clicked.connect(self.habColor)

        self.flagConx = False

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

        self.movAumento = 0.1

        # Valores iniciales de las variables
        self.flagEscritura = False
        self.flagColor = False
        self.visCamera = False

        self.actualButton = []

        self.previusButton = "nan"
        self.datoAuto  = None

        # Imagen de inicio de en lugar de visualizacion de muestras 
        self.img_pixmap = QPixmap("images\microscopio.png")
        self.ui.cameraSpace.setPixmap(self.img_pixmap)

        # Objetos para envio de informacion 
        self.connector = WifiConnector()
        self.send_data = TCP_comunication()
        self.ui.procesador_camara = ProcesadorCamara()
        
        self.R_ = 0
        self.G_ = 0
        self.B_ = 0

        self.ui.pbCamera.clicked.connect(self.cameraSelection)

        self.ui.pbColor.clicked.connect(self.paletteColor) 

        self.ui.tamPincel.currentIndexChanged.connect(self.sizePincel)

        self.ui.tamPincel.setCurrentIndex(1) #Defecto 3px
        

        self.ui.pbCalibrate.setEnabled(False)  
   
        #Boton de guardar pantallas 
        self.ui.pbSave.clicked.connect(self.save)

        ## Elementos en el main 
        # Boton de inicio de conexion
        self.ui.pbConnect.clicked.connect(self.conexion)
        self.original_style = self.ui.pbConnect.styleSheet()

        #Texto inicial de conexion 
        self.ui.txtConnect.setText("No conectado")
        self.ui.txtConnect.setAlignment(Qt.AlignRight)
        # Slider de espectro visible
        self.ui.VisibleEsp.valueChanged.connect(self.slider_value_changed)
        
        # Se crea un objeto connector
        self.connector = WifiConnector()

        #Obejto envio
        self.send_data = TCP_comunication()

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

        self.ui.coordX.returnPressed.connect(self.valueMx)
        self.ui.coordY.returnPressed.connect(self.valueMy)
        self.ui.coordZ.returnPressed.connect(self.valueMz)


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

        # Control de aumento 
         # Crear un grupo de botones
        
        self.ui.aumentoMov.currentIndexChanged.connect(self.aumentoRev)
        self.ui.aumentoMov.setCurrentIndex(0)
        
        self.ui.aumentoGroup.currentIndexChanged.connect(self.aumentoImg)
        self.ui.aumentoGroup.setCurrentIndex(0)

        #ToolTip

        
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

        
        self.ui.procesador_camara.senal_conexion_perdida.connect(self.mostrar_mensaje_conexion_perdida)
    
    def mostrar_mensaje_conexion_perdida(self):

        if self.ui.procesador_camara.conexion_perdida_emitida:
        
            QMessageBox.warning(self, "Error", "Se ha perdido la conexión con la cámara.")
            self.ui.pbConnect.click()

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
        size = (4,10,40,100)
        ind= self.ui.aumentoGroup.currentIndex()
        self.rbuttonAug = size[ind]

        self.sendMotor("G")


    def aumentarX(self):
        self.valueX = self.valueX  + self.movAumento
        self.valueX= self.limitValue(self.valueX)
        self.ui.coordX.setText("{:.3f}".format(self.valueX))
        self.sendMotor("X")


    def disminuirX(self):
        self.valueX = self.valueX - self.movAumento
        self.valueX = self.limitValue(self.valueX)
        self.ui.coordX.setText("{:.3f}".format(self.valueX)) # Muestra siempre con tres cifras decimales
        self.sendMotor("X")

    def aumentarY(self):
        self.valueY = self.valueY  + self.movAumento
        self.valueY= self.limitValue(self.valueY)
        self.ui.coordY.setText("{:.3f}".format(self.valueY))
        self.sendMotor("Y")


    def disminuirY(self):
        self.valueY -= self.movAumento
        self.valueY= self.limitValue(self.valueY)
        self.ui.coordY.setText("{:.3f}".format(self.valueY))
        self.sendMotor("Y")

    def aumentarZ(self):
        self.valueZ = self.valueZ  +  self.movAumento
        self.valueZ= self.limitValue(self.valueZ)
        self.ui.coordZ.setText("{:.3f}".format(self.valueZ))
        self.sendMotor("Z")

    def disminuirZ(self):
        self.valueZ -=  self.movAumento
        self.valueZ= self.limitValue(self.valueZ)
        self.ui.coordZ.setText("{:.3f}".format(self.valueZ))
        self.sendMotor("Z")
    
    def valueMx(self):
        try: 
            value = float(self.ui.coordX.text())
            print("valor X: ", value)
            if value>=0 and value <= 1:
                self.valueX = value
                self.ui.coordX.setText("{:.3f}".format(self.valueX))
                self.sendMotor("X")
            else: 
                value = self.valueX
                self.ui.coordX.setText("{:.3f}".format(self.valueX))

        except ValueError:
            value = self.valueX
            self.ui.coordX.setTqext("{:.3f}".format(self.valueX))


    def valueMy(self):
        
        try:
            value = float(self.ui.coordY.text())
            print("valor Y: ", value)
            if value>=0 and value <= 1:
                self.valueY = value
                self.ui.coordY.setText("{:.3f}".format(self.valueY))
                self.sendMotor("Y")

            else: 
                value = self.valueY
                self.ui.coordY.setText("{:.3f}".format(self.valueY))
      
        except ValueError:
            value = self.valueY
            self.ui.coordY.setText("{:.3f}".format(self.valueY))

    def valueMz(self):
        try:
            value = float(self.ui.coordZ.text())
            print("valor Z: ", value)

            if value>=0 and value <= 1:
                self.valueZ = value
                self.ui.coordZ.setText("{:.3f}".format(self.valueZ))
                self.sendMotor("Z")

            else: 
                value = self.valueZ
                self.ui.coordZ.setText("{:.3f}".format(self.valueZ))
                
        except ValueError:
            value = self.valueZ
            self.ui.coordZ.setText("{:.3f}".format(self.valueZ))


    def aumentoRev(self,indice):
        
        valueSpinbox = [0.1, 0.05, 0.01, 0.005]
        self.movAumento = valueSpinbox[indice]
        
    
    def sendMotor(self,motor):
        if motor == "X": 
            self.valueMotor = str(int(self.valueX*1000)).zfill(9)
        elif motor == "Y":
            self.valueMotor = str(int(self.valueY*1000)).zfill(9) 
        elif motor == "Z":
            self.valueMotor = str(int(self.valueZ*1000)).zfill(9)

        elif motor == "G":
            # self.valueMotor  = "00000000" + str(self.rbuttonAug)

            self.valueMotor = str(self.rbuttonAug).zfill(9)

        self.valueMotor = motor+self.valueMotor

        self.sendHardware(self.valueMotor)

        # self.send_data.send(self.valueMotor)  

     

    def limitValue(self, value):
        
        if value <0:
            return 0
        
        elif value > 1:
            return 1
        
        else: 
            return value

    

    def instruccionesZOE(self):
        ZOEinstruccion = instrucciones()
        ZOEinstruccion.exec_()


    def aboutZOE(self):
        ZOEabout = aboutZOE()
        ZOEabout.exec_()

    def calibrarZOE(self):

        respuesta = QMessageBox.question(self, 'Calibracion', '¿Desea calibrar el sistema ZOE?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if respuesta == True:
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

            if self.connector.is_connected: 
                # self.send_data.close()
                self.ui.pbConnect.click()
                
                QApplication.quit()
            else: 
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
            self.date       = cuadroDatapac.dateImg.date().toString("dd/MM/yyyy")
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
                      "aum4x","aum10x","aum40x","aum100x", "aumentoMov","coordX","coordY", "coordZ", "plusX","plusY", "plusZ", "minusX", "minusY", "minusZ")

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
                    self.sendHardware("A"+self.datoAuto)
                    
                    print("A"+self.datoAuto)
                   

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
                 
                self.sendHardware("M" + str(self.ui.value) +  "000000" )
                
                
            if radio_button.text() == 'A':
           
                if self.datoAuto != None:
                    

                    self.sendHardware("A"+self.datoAuto )
                    
                    print("A"+self.datoAuto)


            if radio_button.text() == 'W':
                # Se limitan y paran todas las acciones 
                 
                self.sendHardware("W000000000")
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
            
            self.sendHardware("M" + str(value) +  "000000")
            
        
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


    

    # Proceso de conexion del pc-esp32
    def conexion(self):

        if self.connector.is_connected:     #Revisa el atributo en el constructor
            
            if self.respuestaCon != True:
                self.ui.RB_white.setChecked(True)

                if self.flagConx == False:
                    
                    self.sendHardware("D000000000")

                    
                    # self.cerrado = self.send_data.close()
                    self.flagConx = True
                    self.cerrado = True
                    time.sleep(0.5)

            else: 
                self.cerrado = True

            
            
            if self.cerrado:
                
                if not self.connector.disconnect() :

                    self.flagConx   = False
                    self.cerrado    = False
                
                    #Revisa los retornos de los metodos 
                    self.ui.pbCamera.setEnabled(True)
                    self.ui.pbConnect.setText('C')
                    
                    self.ui.pbConnect.setStyleSheet(self.original_style)
                    self.ui.txtConnect.setText("Desconexión exitosa")
                    self.ui.txtConnect.setAlignment(Qt.AlignRight)

                    
                    self.ui.RB_manual.setChecked(False)
                    self.ui.RB_auto.setChecked(False)
                    
                    self.ui.RB_manual.setEnabled(False)
                    self.ui.RB_auto.setEnabled(False)
                    self.ui.RB_white.setEnabled(False)
                    self.ui.wavelength.setEnabled(False)
                    self.ui.VisibleEsp.setEnabled(False) 
                    self.ui.aumentoGroup.setEnabled(False)
                    self.ui.pbCalibrate.setEnabled(False)            

                    self.visCamera = False

                # Desactivamos botones 
                    self.manejoButton(False)

                    if self.previusNamebutton != None:
                        self.funcionHab[self.previusNamebutton]()
                        self.actualButton.setStyleSheet("")
                        
                    self.previusButton = None
                    self.previusNamebutton = None

                    # Limpiar la pantalla  para vovler a la imagen inicial
                    self.ui.tablero.clear()

                else:
                    self.ui.txtConnect.setText("No se pudo desconectar")
                    self.ui.txtConnect.setAlignment(Qt.AlignRight)

                    self.manejoButton(False)
                    

        else:
            if self.connector.connect():
                self.ui.pbConnect.setText('C')
                self.ui.pbConnect.setStyleSheet(""" background-color: rgb(50, 255, 50); """ )
                
                self.ui.txtConnect.setText("Conexión establecida")
                self.ui.txtConnect.setAlignment(Qt.AlignRight)

                # Encendemos los botonoes 

                
               
                self.manejoButton(True)
                self.ui.actionCalibrar.setEnabled(True)

                self.ui.pbCamera.setEnabled(False)
                self.ui.VisibleEsp.setEnabled(False)     

                self.ui.procesador_camara.iniciar_camara()
                self.ui.procesador_camara.senal_actualizacion.connect(self.actualizar_interfaz)
                
                self.visCamera = True
                self.ui.aumentoGroup.setEnabled(True)

                self.ui.RB_manual.setEnabled(True)
                self.ui.pbCalibrate.setEnabled(True)      
                
                self.ui.RB_white.setEnabled(True)
                
                # Realiza la conexion 
                self.send_data.connect()

                if self.datoAuto == None:
                    self.ui.RB_auto.setEnabled(False)

            else:
                self.ui.txtConnect.setText("No se pudo establecer la conexión")
                self.ui.txtConnect.setAlignment(Qt.AlignRight)

    def guardar_variable(self,variable,archivo):
        with open(archivo, 'w') as archivo:
            archivo.write(variable)

    def sendHardware(self, dato):
        print(dato)
        self.respuestaCon = self.send_data.send(dato)  

        if self.respuestaCon: 
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("No es posible enviar datos. Revisa la conexión")
            msg.setWindowTitle("Conexión")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

            self.ui.pbConnect.setStyleSheet(""" background-color: rgb(255,255,0); """ )
            self.ui.txtConnect.setText("Error de conexión")
            
            
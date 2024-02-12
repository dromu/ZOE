import sys
from PyQt5 import uic, QtWidgets
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QPoint
from img_tools.CameraView import ProcesadorCamara

from PyQt5.QtWidgets import QFileDialog, QActionGroup,QAction,QButtonGroup
import numpy as np 
import os
import cv2 
from PyQt5.QtWidgets import QApplication, QDialog,QMessageBox
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSlider, QLabel
from PyQt5.QtMultimedia import QCameraInfo

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

        self.ui.barraInfo.textChanged.connect(self.actualizarTexto)
        # self.ui.pbArrow.clicked.connect(self.ui.tablero.habArrow)

        self.ui.checkPaciente.stateChanged.connect(self.datosPacientes)

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

        self.nombre         = ""
        self.identificacion = ""
        self.modalidad      = ""
        self.textImage      = ""
        self.cerrado = False

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


        # Conexion de las herramientas de la barra de tareas 
        color_actions = {
            self.ui.blueAction: "blue",
            self.ui.redAction: "red",
            self.ui.greenAction: "green",
            self.ui.blackAction: "black",
            self.ui.yellowAction: "yellow",
            self.ui.whiteAction: "white",
        }
        

        for action, color in color_actions.items():
            action.triggered.connect(lambda _, c=color: self.ui.tablero.pincelColor(c))

        size_actions = {
            self.ui.onepxAction: 1,
            self.ui.threepxAction:3,
            self.ui.fivepxAction: 5,
            self.ui.sevenpxAction: 7,
            self.ui.ninepxAction: 9
        }
        
        self.rbuttonAug = 0
        
        grupo_tamanos_pincel = QActionGroup(self)
        

        for actionSize, tamsize in size_actions.items():
            actionSize.setCheckable(True)
            grupo_tamanos_pincel.addAction(actionSize)
            actionSize.triggered.connect(lambda _,dim=tamsize: self.ui.tablero.pincelSize(dim))
       
   
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
        self.ui.zoeDev.triggered.connect(self.aboutZOE)
        self.ui.actionCalibrar.triggered.connect(self.calibrarZOE)
        self.ui.actionInstrucciones.triggered.connect(self.instruccionesZOE)
        self.ui.actionClose.triggered.connect(self.exitSystem)

        cameras = QCameraInfo.availableCameras()
        self.camera_group = QActionGroup(self)
        self.camera_group.setExclusive(True)

        # Mostrar los nombres de las cámaras en el menú
    
        for camera in cameras:
            action = QAction(camera.description(), self)
            action.setCheckable(True)
            self.camera_group.addAction(action)
            action.triggered.connect(self.camera_selected)  # Conectar la función al evento triggered
            self.ui.menuCamara.addAction(action)

        if self.camera_group.actions():
            ind = self.readCamera()
            self.camera_group.actions()[ind].setChecked(True)


        #   CONTROL DE MOTORES 
        #   Aumento del mov    
        self.movAumento = 0.005
        valueSpinbox = [0.005,0.01,0.05,0.1]
        self.ui.aumentoMov.setRange(0, len(valueSpinbox)-1)
        self.ui.aumentoMov.setPageStep(1)
        self.ui.aumentoMov.setTickInterval(1)
        self.ui.aumentoMov.setTickPosition(QSlider.TicksBelow)
        self.ui.aumentoMov.valueChanged.connect(self.aumentoRev)
        self.ui.textAumento.setText("{:.3f}".format(self.movAumento))
        
        


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
        self.aumentoGroup = QButtonGroup(self)

        self.aumentoGroup.addButton(self.ui.aum4x)
        self.aumentoGroup.addButton(self.ui.aum10x)
        self.aumentoGroup.addButton(self.ui.aum40x)
        self.aumentoGroup.addButton(self.ui.aum100x)

        # Conectar la señal de cambio para manejar eventos
        self.aumentoGroup.buttonClicked.connect(self.aumentoImg)


    def aumentoImg(self,botonR):
        
        augment  = botonR.text()
        print(augment)
        print(type(augment))

        if augment == "4X":
            self.rbuttonAug = 0
        if augment == "10X":
            self.rbuttonAug = 1
        if augment == "40X":
            self.rbuttonAug = 2
        if augment == "100X":
            self.rbuttonAug = 3

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
        valueSpinbox = [0.005,0.01,0.05,0.1]
        self.movAumento = valueSpinbox[indice]
        self.ui.textAumento.setText("{:.3f}".format(self.movAumento))
    
    def sendMotor(self,motor):
        if motor == "X": 
            self.valueMotor = str(int(self.valueX*1000)).zfill(9)
        elif motor == "Y":
            self.valueMotor = str(int(self.valueY*1000)).zfill(9) 
        elif motor == "Z":
            self.valueMotor = str(int(self.valueZ*1000)).zfill(9)

        elif motor == "G":
            self.valueMotor  = "00000000" + str(self.rbuttonAug)

        self.valueMotor = motor+self.valueMotor

        self.send_data.send(self.valueMotor)  

        print(self.valueMotor)

    def limitValue(self, value):
        
        if value <0:
            return 0
        
        elif value > 1:
            return 1
        
        else: 
            return value

    def camera_selected(self):
        selected_camera = None
        indCamera = None

        # Buscar la cámara seleccionada
        for i, action in enumerate(self.camera_group.actions()):
            if action.isChecked():
                selected_camera = action.text()
                indCamera = i
                break

        # Guardar la variable seleccionada (aquí puedes hacer lo que necesites con selected_camera)
        if selected_camera:
            print(f"Cámara seleccionada: {selected_camera}")
            dataCamera = str(indCamera)+str(selected_camera)
            self.guardar_variable(dataCamera,"img_tools/camera.dat" )

    def instruccionesZOE(self):
        ZOEinstruccion = instrucciones()
        ZOEinstruccion.exec_()


    def aboutZOE(self):
        ZOEabout = aboutZOE()
        ZOEabout.exec_()

    def calibrarZOE(self):

        respuesta = QMessageBox.question(self, 'Calibracion', '¿Desea calibrar el sistema ZOE?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if respuesta:
            self.send_data.send("K"+"000000000") 
            
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
                self.send_data.close()
                self.ui.pbConnect.click()
                
                QApplication.quit()
            else: 
                QApplication.quit()
            
            




    
    def datosPacientes(self,state):
        
        if state == Qt.Checked:  # Estado 2 significa que el QCheckBox está marcado (Qt.Checked)
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

                #EQUIPO
                self.institucion    = cuadroDatapac.insEqu.text()
                self.nameEquipo    = cuadroDatapac.nameEqu.text()

                if self.posPaciente == "Si":
                    self.posPaciente = [str(int(self.valueX*1000)), str(int(self.valueY*1000)),str(int(self.valueZ*1000))]

                else:
                    self.posPaciente = ""

                

                
            else:
                state = Qt.Unchecked  # Cambiar el valor de state a Qt.Unchecked
                self.ui.checkPaciente.setChecked(state) 
                
                
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

    def actualizarTexto(self):
        self.textImage = self.ui.barraInfo.text()
        


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
        buttonName = ("pbDot","pbRect","pbHide","pbTrash", "pbElip", "pbText", "pbDel", "pbROI", "pbSave", "pbArrow", "pbBack", "pbForw",
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
                    self.send_data.send("A"+self.datoAuto) 
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
            
            dataset.StudyDescription = self.textImage

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
            
            if radio_button.text() == 'Manual':
                # Se habilitan todas las modificaciones al espectro 
                slider.setEnabled(True)    
                wavelength.setEnabled(True)    
                
            
            
                # Envio en modo manual
                self.send_data.send("M" + str(self.ui.value) +  "000000" )  
                print("M" + str(self.ui.value) +  "000000" )
                
                
            if radio_button.text() == 'Automático':
           
                if self.datoAuto != None:
                    self.send_data.send("A"+self.datoAuto) 
                    print("A"+self.datoAuto)
                    


            if radio_button.text() == 'Luz blanca':
                # Se limitan y paran todas las acciones 
                self.send_data.send("W000000000" ) 
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
            self.send_data.send("M" + str(value) +  "000000" )  
            print("M" + str(value) +  "000000" )
        
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
            self.cerrado = self.send_data.close()

            print("isConnect")

            if self.cerrado == True :
                self.ui.RB_white.setChecked(False)

                print("Cerrado")

                if not self.connector.disconnect() :
                
                    #Revisa los retornos de los metodos 
                    self.ui.menuCamara.setEnabled(True)
                    self.ui.pbConnect.setText('Conectar')
                    
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
                self.cerrado = False

        else:
            if self.connector.connect():
                self.ui.pbConnect.setText('Conectado')
                self.ui.pbConnect.setStyleSheet(""" font: 75 16pt "MS Shell Dlg 2";
                                                    background-color: rgb(50, 255, 50);
                                                    padding: 8px;
                                                    border-radius: 10px;
                                                    color: rgb(0,0,0);
                                                    border-color: rgb(0, 0, 0);
                                                    """ )
                
                self.ui.txtConnect.setText("Conexión establecida")
                self.ui.txtConnect.setAlignment(Qt.AlignRight)

                # Encendemos los botonoes 
               
                self.manejoButton(True)
                self.ui.actionCalibrar.setEnabled(True)

                self.ui.menuCamara.setEnabled(False)

                self.ui.procesador_camara.iniciar_camara()
                self.ui.procesador_camara.senal_actualizacion.connect(self.actualizar_interfaz)
                
                self.visCamera = True

                self.ui.RB_manual.setEnabled(True)
                
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
        
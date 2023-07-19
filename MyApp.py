import sys
from PyQt5 import uic, QtWidgets
from wificonnector import WifiConnector
from TCP_comunication2 import TCP_comunication
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from CameraThread import CameraThread
from PyQt5.QtMultimedia import QCameraInfo

from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QMenu

qtCreatorFile = "zoe_main.ui"  # Nombre del archivo aquí.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.camera_menu = QMenu("Cámara", self)
        self.populate_camera_menu()

        menubar = self.menuBar()
        menubar.addMenu(self.camera_menu)
    
        self.camera_thread = CameraThread()
        self.camera_thread.frame_data.connect(self.display_frame)

        ## Elementos en el main 
        # Boton de inicio de conexion
        self.BuConnect.setStyleSheet("QPushButton { background-color: red;  }")
        self.BuConnect.clicked.connect(self.conexion)
        #Texto inicial de conexion 
        self.TextConnect.setText("No conectado")
        # Slider de espectro visible
        self.VisibleEsp.valueChanged.connect(self.slider_value_changed)
        
        # Se crea un objeto connector
        self.connector = WifiConnector()

        #Obejto envio
        self.send_data = TCP_comunication()
        
        # Deshabilitamos los elementos del main, estos se iran actualizando
        self.wavelength.setEnabled(False)
        self.VisibleEsp.setEnabled(False)
        self.RB_manual.setEnabled(False)
        self.RB_auto.setEnabled(False)
        self.RB_white.setEnabled(False)

        # Cambiar el valor del slider en texto
        self.wavelength.returnPressed.connect(self.line_edit_return_pressed)

        # Seleccion de modo luz blanca por defecto
        self.RB_white.setChecked(True)

        self.RB_manual.toggled.connect(lambda: self.processRadioButton(self.RB_manual, self.VisibleEsp, self.wavelength))
        self.RB_auto.toggled.connect(lambda: self.processRadioButton(self.RB_auto, self.VisibleEsp,self.wavelength))
        self.RB_white.toggled.connect(lambda: self.processRadioButton(self.RB_white, self.VisibleEsp,self.wavelength))

        self.value = 380

    def populate_camera_menu(self):
        available_cameras = QCameraInfo.availableCameras()

        self.camera_menu.clear()

        for camera_info in available_cameras:
            camera_name = camera_info.description()
            action = QAction(camera_name, self)
            action.triggered.connect(lambda checked, camera_info=camera_info: self.on_camera_selected(camera_info))
            self.camera_menu.addAction(action)

    def on_camera_selected(self, camera_info):
        print(f"Cámara seleccionada: {camera_info.description()}")
      
            

    def display_frame(self, frame):
        pixmap = QPixmap.fromImage(frame)
        self.cameraCV.setPixmap(pixmap)


    def processRadioButton(self, radio_button, slider, wavelength):
        if radio_button.isChecked():

            print(radio_button.text())
            
            if radio_button.text() == 'Manual':
                # Se habilitan todas las modificaciones al espectro 
                slider.setEnabled(True)    
                wavelength.setEnabled(True)    
                
                
            if radio_button.text() == 'Automático':
                self.value = 500
                self.send_data.send("A"+str(self.value))  
                # self.send_data.send(str(self.value) )  

                # ACtualizamos el valor directamente, con el obtenido del cambio de espacio 
                self.wavelength.setText(str(self.value))

                # Se limitan las acciones para que no se pueda mover la longitud
                self.wavelength.setEnabled(False)
                self.VisibleEsp.setEnabled(False)
               
            if radio_button.text() == 'Luz blanca':
                # Se limitan y paran todas las acciones 
                self.send_data.send("W"+str(self.value)) 
                self.wavelength.setEnabled(False)
                self.VisibleEsp.setEnabled(False)
                
            slider.setValue(self.value)
           
    # Recibe los valores de cambio del slider
    def slider_value_changed(self, value):
        # Checkea el boton manual
        if self.RB_manual.isChecked():
            self.wavelength.setText(str(value))
            self.value = int(value) # ACtualizamos el valor para que la barra quede en el mismo punto del manual
            print(str(value))
            self.send_data.send("M" + str(value) )  
        else:
            # Se deshabilita cualquier accion diferente
            self.wavelength.setEnabled(False)
            self.VisibleEsp.setEnabled(False)

    # Hace referencia al recuadro para cambio de longitud
    def line_edit_return_pressed(self):
        value = self.wavelength.text()
        if value.isdigit():
            value = int(self.wavelength.text())
            if 380 <= value <= 780:
                self.VisibleEsp.setValue(value)
            else:
                self.wavelength.setText("Invalid value!")
        else:
                self.wavelength.setText("Invalid value!")

    # Proceso de conexion del pc-esp32
    def conexion(self):
        if self.connector.is_connected:     #Revisa el atributo en el constructor

            
            if not self.connector.disconnect(): #Revisa los retornos de los metodos 
                self.BuConnect.setText('Conectar')
                self.BuConnect.setStyleSheet("QPushButton { background-color: red; }")
                self.TextConnect.setText("Desconexión exitosa")

                self.RB_manual.setEnabled(False)
                self.RB_auto.setEnabled(False)
                self.RB_white.setEnabled(False)
                self.wavelength.setEnabled(False)
                self.VisibleEsp.setEnabled(False)

            else:
                self.TextConnect.setText("No se pudo desconectar.")

        else:
            if self.connector.connect():
                self.BuConnect.setText('Conectado')
                self.BuConnect.setStyleSheet("QPushButton { background-color: green; }")
                self.TextConnect.setText("Conexión establecida.")
                
                self.camera_thread.start()
                self.RB_manual.setEnabled(True)
                self.RB_auto.setEnabled(True)
                self.RB_white.setEnabled(True)
                
                # Realiza la conexion 
                self.send_data.connect()
            else:
                self.TextConnect.setText("No se pudo establecer la conexión.")
                

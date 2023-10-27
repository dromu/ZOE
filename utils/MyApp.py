import sys
from PyQt5 import uic, QtWidgets
from comunication.wificonnector import WifiConnector
from comunication.TCP_comunication import TCP_comunication
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from img_tools.CameraThread import CameraThread
from PyQt5.QtMultimedia import QCameraInfo
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QMenu
from PyQt5.QtCore import QSize
from PyQt5.QtCore import Qt
import numpy as np
import cv2

qtCreatorFile = "gui\zoe_main.ui"  # Nombre del archivo aquí.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

# La clase `MyApp` es una aplicación PyQt que muestra una transmisión de la cámara y permite al
# usuario controlar la configuración de la cámara y establecer una conexión con un dispositivo ESP32.
class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        """
        La función `populate_camera_menu` borra el menú de la cámara y lo completa con las cámaras
        disponibles.
        """

        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # Se crea un menu para mostrar las distintas camaras
        self.camera_menu = QMenu("Cámara", self)
        self.populate_camera_menu()
        menubar = self.menuBar()
        menubar.addMenu(self.camera_menu)

    
        # El código crea una instancia de la clase `CameraThread` y la asigna a la variable
        # `self.camera_thread`. Luego conecta la señal `frame_data` del `camera_thread` al método
        # `display_frame`. Esto permite llamar al método `display_frame` siempre que haya un nuevo
        # cuadro disponible en el hilo de la cámara.
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


        self.pushButton_10.clicked.connect(self.zoom_plus)

        self.value = 380
        # self.camera_thread.start()


    def zoom_plus(self, frame):
        # Generar coordenadas aleatorias dentro de las dimensiones de la imagen
        x = np.random.randint(0, 640)
        y = np.random.randint(0, 480)

        # Color del punto en formato BGR (azul, verde, rojo)
        color_punto = (0, 255, 0)  # verde

        imagen_np = np.array(frame)

        print(imagen_np.shape)
        

        # Dibujar el punto en la imagen
        cv2.circle(imagen_np, (x, y), 5, color_punto, -1)  # -1 para rellenar el círculo
    
        imagen_qt = QImage(imagen_np.data, imagen_np.shape[1], imagen_np.shape[0], imagen_np.shape[1] * 3, QImage.Format_RGB888)

        self.camera_thread.image_qt.connect(self.display_frame)

    def populate_camera_menu(self):
        """
        La función completa un menú con cámaras disponibles y conecta cada cámara a una función de
        devolución de llamada.
        """
        available_cameras = QCameraInfo.availableCameras()

        self.camera_menu.clear()

        for camera_info in available_cameras:
            camera_name = camera_info.description()
            action = QAction(camera_name, self)
            action.triggered.connect(lambda checked, camera_info=camera_info: self.on_camera_selected(camera_info))
            self.camera_menu.addAction(action)

    def on_camera_selected(self, camera_info):
        """
        La función "on_camera_selected" imprime la descripción de la cámara seleccionada.
        
        Args:
          camera_info: El parámetro "camera_info" es un objeto que contiene información sobre la cámara
        seleccionada. Probablemente tenga propiedades como "nombre", "resolución", "fabricante", etc.
        """
        print(f"Cámara seleccionada: {camera_info.description()}")
      
            

    def display_frame(self, frame):
        """
        La función muestra un marco en un widget QLabel en una aplicación PyQt.
        
        Args:
          frame: El parámetro `frame` es un marco de imagen que se pasa al método `display_frame`. Se
        espera que esté en un formato que pueda convertirse en un objeto `QPixmap` usando el método
        `fromImage` de la clase `QPixmap`.
        """

        # Se redimensiona el tamaño de la imagen de entrada 
        tamaño = QSize(1100,800)
        imagen_redimensionada = frame.scaled(
            tamaño, 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )

       # El código está creando un objeto QPixmap llamado `pixmap` a partir de la imagen
       # redimensionada `imagen_redimensionada`. El método `fromImage` de la clase QPixmap se utiliza
       # para convertir el objeto QImage en un objeto QPixmap.
        pixmap = QPixmap.fromImage(imagen_redimensionada)
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
                

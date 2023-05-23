import sys
from PyQt5 import uic, QtWidgets
from wificonnector import WifiConnector


qtCreatorFile = "zoe_main.ui"  # Nombre del archivo aquí.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # Boton de inicio de conexion
        self.BuConnect.setStyleSheet("QPushButton { background-color: red;  }")
        self.BuConnect.clicked.connect(self.conexion)
        
        #Texto inicial de conexion 
        self.TextConnect.setText("No conectado")
        
        # Se crea un objeto connector
        self.connector = WifiConnector()

        # Slider de espectro visible
        self.VisibleEsp.valueChanged.connect(self.slider_value_changed)

        # Cambiar el valor del slider en texto
        self.wavelength.returnPressed.connect(self.line_edit_return_pressed)

    def slider_value_changed(self, value):
        self.wavelength.setText(str(value))

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

    def conexion(self):
        if self.connector.is_connected:     #Revisa el atributo en el constructor
            if not self.connector.disconnect(): #Revisa los retornos de los metodos 
                self.BuConnect.setText('Conectar')
                self.BuConnect.setStyleSheet("QPushButton { background-color: red; }")
                self.TextConnect.setText("Desconexión exitosa")
            else:
                self.TextConnect.setText("No se pudo desconectar.")

        else:
            if self.connector.connect():
                self.BuConnect.setText('Conectado')
                self.BuConnect.setStyleSheet("QPushButton { background-color: green; }")
                self.TextConnect.setText("Conexión establecida.")
            else:
                self.TextConnect.setText("No se pudo establecer la conexión.")

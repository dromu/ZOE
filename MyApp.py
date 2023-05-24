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

        # Deshabilitamos el slider y el label que muestra lambda
        self.wavelength.setEnabled(False)
        self.VisibleEsp.setEnabled(False)

        # Cambiar el valor del slider en texto
        self.wavelength.returnPressed.connect(self.line_edit_return_pressed)

        # Seleccion de modo luz blanca por defecto
        self.RB_white.setChecked(True)


        self.RB_manual.toggled.connect(lambda: self.processRadioButton(self.RB_manual, self.VisibleEsp, self.wavelength))
        self.RB_auto.toggled.connect(lambda: self.processRadioButton(self.RB_auto, self.VisibleEsp,self.wavelength))
        self.RB_white.toggled.connect(lambda: self.processRadioButton(self.RB_white, self.VisibleEsp,self.wavelength))

        self.value = 380
    
    def processRadioButton(self, radio_button, slider, wavelength):
        if radio_button.isChecked():

            print(radio_button.text())
            
            if radio_button.text() == 'Manual':
                slider.setEnabled(True)    
                wavelength.setEnabled(True)       
                
            if radio_button.text() == 'Automático':
                self.value = 500
                self.wavelength.setEnabled(False)
                self.VisibleEsp.setEnabled(False)
               
            if radio_button.text() == 'Luz blanca':
                self.wavelength.setEnabled(False)
                self.VisibleEsp.setEnabled(False)
                
            slider.setValue(self.value)
           

    def slider_value_changed(self, value):
        if self.RB_manual.isChecked():
            self.wavelength.setText(str(value))
            self.value = int(value) # ACtualizamos el valor para que la barra quede en el mismo punto del manual
            print(str(value))
            self.wavelength.setEnabled(True)
            
        else:
            self.wavelength.setEnabled(False)
            self.VisibleEsp.setEnabled(False)


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

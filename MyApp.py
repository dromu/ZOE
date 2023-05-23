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
        self.BuConnect.setStyleSheet("QPushButton { background-color: red;  }")
        self.BuConnect.clicked.connect(self.conexion)

        self.TextConnect.setText("No conectado")
        
        # Se crea un objeto connector
        self.connector = WifiConnector()

    def conexion(self):
        if self.connector.is_connected:     #Revisa el atributo en el constructor
            if not self.connector.disconnect():
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


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())

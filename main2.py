import sys
from PyQt5 import uic, QtWidgets

qtCreatorFile = "zoe_main.ui" # Nombre del archivo aquí.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.BuConnect.setStyleSheet("QPushButton { background-color: red;  }")
        self.BuConnect.clicked.connect(self.conexion)        
        self.is_connected = False

    def conexion(self):
        if self.is_connected:
            self.BuConnect.setText('Conectar')
            self.BuConnect.setStyleSheet("QPushButton { background-color: red; }")
        else:
            self.BuConnect.setText('Conectado')
            self.BuConnect.setStyleSheet("QPushButton { background-color: green; }")
        self.is_connected = not self.is_connected      

if __name__ == "__main__":
    app =  QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
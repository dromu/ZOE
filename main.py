import sys
from PyQt5 import QtWidgets
from utils.MyApp import MyApp

sys.path.append("utils")
# El bloque `if __name__ == "__main__":` es un modismo común utilizado en Python para garantizar que
# el código que contiene solo se ejecute cuando el script se ejecuta directamente y no cuando se
# importa como un módulo.

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.showMaximized()
    sys.exit(app.exec_())

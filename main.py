import sys
from PyQt5 import QtWidgets
from utils.MyApp import MyApp

sys.path.append("utils")
# El bloque `if __name__ == "__main__":` es un modismo común utilizado en Python para garantizar que
# el código que contiene solo se ejecute cuando el script se ejecuta directamente y no cuando se
# importa como un módulo.

def run_zoe():
    """
    La función `run_zoe` crea una instancia de la clase `MyApp`, maximiza la ventana e inicia el bucle
    de eventos de la aplicación.  
    """
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.showMaximized()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run_zoe()

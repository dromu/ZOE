import sys
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.uic import loadUi

class instrucciones(QDialog):
    def __init__(self):
        super(instrucciones, self).__init__()
        loadUi("gui\instruccion.ui", self)  # Carga el archivo .ui en el diálogo
        self.setWindowTitle("Instrucciones")

    
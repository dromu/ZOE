import sys
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.uic import loadUi
from PyQt5.QtCore import QDate

class dataPaciente(QDialog):
    def __init__(self):
        super(dataPaciente, self).__init__()
        loadUi("gui\zoePaciente.ui", self)  # Carga el archivo .ui en el diálogo
        self.setWindowTitle("Acerca de ZOE")

        
        self.dateImg.setDate(QDate.currentDate())
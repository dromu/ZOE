import sys
from PyQt5.QtWidgets import QApplication, QDialog, QFormLayout, QLineEdit, QPushButton, QLabel

class dataPaciente(QDialog):
    def __init__(self, parent=None):
        super(dataPaciente, self).__init__(parent)

        # Crear tres QLineEdit
        self.line_edit_nombre = QLineEdit(self)
        self.line_edit_identificacion = QLineEdit(self)
        self.line_edit_modalidad = QLineEdit(self)

        # Crear etiquetas correspondientes
        etiqueta_nombre = QLabel('Nombre paciente:')
        etiqueta_identificacion = QLabel('Identificación:')
        etiqueta_modalidad = QLabel('Modalidad:')

        # Crear botones de Aceptar y Cancelar
        self.boton_aceptar = QPushButton('Aceptar', self)
        self.boton_cancelar = QPushButton('Cancelar', self)

        # Conectar los botones a las funciones correspondientes
        self.boton_aceptar.clicked.connect(self.aceptar_clicked)
        self.boton_cancelar.clicked.connect(self.cancelar_clicked)

        # Crear un diseño de formulario
        layout = QFormLayout()
        layout.addRow(etiqueta_nombre, self.line_edit_nombre)
        layout.addRow(etiqueta_identificacion, self.line_edit_identificacion)
        layout.addRow(etiqueta_modalidad, self.line_edit_modalidad)
        layout.addRow(self.boton_aceptar, self.boton_cancelar)

        # Establecer el diseño para el cuadro de diálogo
        self.setLayout(layout)

        self.setWindowTitle('Cuadro de Diálogo')

    def aceptar_clicked(self):
        # Lógica para el botón Aceptar
        print('Botón Aceptar clickeado')
        self.accept()

    def cancelar_clicked(self):
        # Lógica para el botón Cancelar
        print('Botón Cancelar clickeado')
        self.reject()


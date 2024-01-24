import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QCheckBox, QPushButton, QLabel

class VentanaPrincipal(QDialog):
    def __init__(self):
        super(VentanaPrincipal, self).__init__()

        # Crear un QCheckBox
        self.checkbox = QCheckBox('Abrir Cuadro de Diálogo', self)
        self.checkbox.stateChanged.connect(self.mostrar_cuadro_dialogo)

        # Crear un botón de salida
        self.boton_salir = QPushButton('Salir', self)
        self.boton_salir.clicked.connect(self.close)

        # Diseño vertical
        layout = QVBoxLayout()
        layout.addWidget(self.checkbox)
        layout.addWidget(self.boton_salir)
        self.setLayout(layout)

        self.setWindowTitle('Ventana Principal')

    def mostrar_cuadro_dialogo(self, state):
        if state == 2:  # Estado 2 significa que el QCheckBox está marcado (Qt.Checked)
            cuadro_dialogo = CuadroDialogo(self)
            cuadro_dialogo.exec_()

class CuadroDialogo(QDialog):
    def __init__(self, parent=None):
        super(CuadroDialogo, self).__init__(parent)

        # Crear etiqueta en el cuadro de diálogo
        etiqueta = QLabel('¡Cuadro de Diálogo Abierto!', self)

        # Diseño vertical
        layout = QVBoxLayout()
        layout.addWidget(etiqueta)
        self.setLayout(layout)

        self.setWindowTitle('Cuadro de Diálogo')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana_principal = VentanaPrincipal()
    ventana_principal.show()
    sys.exit(app.exec_())

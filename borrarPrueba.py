import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt5.QtGui import QColor

class BotonesApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.botones = []

        # Crear cinco botones
        for i in range(5):
            boton = QPushButton(f'Botón {i+1}', self)
            boton.clicked.connect(lambda _, idx=i: self.cambiarColor(idx))
            self.botones.append(boton)

        # Diseño vertical
        layout = QVBoxLayout()
        for boton in self.botones:
            layout.addWidget(boton)

        self.setLayout(layout)

        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('Botones con PyQt5')
        self.show()

    def cambiarColor(self, idx):
        # Restaurar el color original de los botones
        for i, boton in enumerate(self.botones):
            if i == idx:
                # Cambiar el color del botón presionado
                boton.setStyleSheet("background-color: green")
            else:
                # Restaurar el color original de los demás botones
                boton.setStyleSheet("")

def main():
    app = QApplication(sys.argv)
    ventana = BotonesApp()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

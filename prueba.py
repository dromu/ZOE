import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QInputDialog, QLabel


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.button = QPushButton('Seleccionar tamaño del pincel', self)
        self.button.clicked.connect(self.showInputDialog)
        layout.addWidget(self.button)

        self.label = QLabel('Tamaño del pincel: 1', self)
        layout.addWidget(self.label)

        self.setLayout(layout)

        self.setWindowTitle('Ventana principal')

    def showInputDialog(self):
        size, okPressed = QInputDialog.getInt(self, "Tamaño del pincel", "Ingrese el tamaño del pincel:", 1, 1, 100, 1)
        if okPressed:
            self.label.setText(f'Tamaño del pincel: {size}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

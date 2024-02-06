import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer

class calibration:
    def __init__(self):
        self.app = QApplication(sys.argv)

    def show_please_wait_message(self):
        # Crear el QMessageBox
        self.msg_box = QMessageBox()
        self.msg_box.setWindowTitle("Por favor, espera")
        self.msg_box.setText("Calibrando...")
        self.msg_box.setIcon(QMessageBox.Warning)
        # self.msg_box.setStandardButtons(QMessageBox.NoButton)

        # Mostrar el QMessageBox
        self.msg_box.show()

        # Configurar un temporizador para cerrar el QMessageBox después de 10 segundos
        timer = QTimer()
        timer.singleShot(1000, self.close_message_box)

        # Ejecutar la aplicación
        sys.exit(self.app.exec_())

    def close_message_box(self):
        self.msg_box.close()

if __name__ == "__main__":
    message_box = calibration()
    message_box.show_please_wait_message()


import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer

def show_information_box():
    app = QApplication(sys.argv)
    message_box = QMessageBox(QMessageBox.Information, "Calibracion", "¿Desea calibrar el sistema ZOE?")

    # Mostrar el QMessageBox sin botones
    message_box.setStandardButtons(QMessageBox.NoButton)
    message_box.show()

    # Cerrar automáticamente después de 2 segundos (2000 milisegundos)
    QTimer.singleShot(2, message_box.close)

    sys.exit(app.exec_())

if __name__ == "__main__":
    show_information_box()

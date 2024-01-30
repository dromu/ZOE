import sys
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.uic import loadUi

class aboutZOE(QDialog):
    def __init__(self):
        super(aboutZOE, self).__init__()
        loadUi("gui\ZOEabout.ui", self)  # Carga el archivo .ui en el diálogo
        self.setWindowTitle("Acerca de ZOE")

    

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     my_dialog = MyDialog()
    
#     if my_dialog.exec_() == QDialog.Accepted:
#         print("Botón OK presionado.")
    
#     sys.exit(app.exec_())

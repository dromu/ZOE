from PyQt5.QtWidgets import QApplication, QDialog, QFormLayout, QLineEdit, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt

class CustomInputDialog(QDialog):
    def __init__(self, parent=None):
        super(CustomInputDialog, self).__init__(parent)

        self.setWindowTitle("Etiquetado")

        # Crear un diseño de formulario
        layout = QFormLayout(self)

        # Agregar un campo de entrada personalizado al diseño
        input_widget = QLineEdit(self)

        

        input_widget.setStyleSheet("""
            background-color: #F0F0F0;
            border: 1px solid #CCCCCC;
            border-radius: 5px;
            padding: 5px 70px;
            padding-left: 0;
            padding-right: 0
         

        """)
        layout.addRow("Ingrese texto:", input_widget)
        layout.setLabelAlignment(Qt.AlignCenter)

        

        

        # Agregar botones OK y Cancelar
        ok_button = QPushButton("OK", self)
        ok_button.setStyleSheet("""
            background-color: #4CAF50;
            color: white;
            padding: 5px 90px;
            border: none;
            border-radius: 3px;
        """)
        ok_button.clicked.connect(self.accept)

        cancel_button = QPushButton("Cancelar", self)
        cancel_button.setStyleSheet("""
            background-color: #CCCCCC;
            color: black;
            padding: 5px 100px;
            border: none;
            border-radius: 3px;
        """)
        cancel_button.clicked.connect(self.reject)

        layout.addRow(ok_button, cancel_button)



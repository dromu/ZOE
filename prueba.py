import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # QLineEdit para ingresar valores flotantes
        self.coord_z_line_edit = QLineEdit()
        layout.addWidget(self.coord_z_line_edit)

        # Botón para obtener y procesar el valor flotante
        process_button = QPushButton("Procesar Valor")
        process_button.clicked.connect(self.process_value)
        layout.addWidget(process_button)

        self.setLayout(layout)
        self.setWindowTitle("Ejemplo de Valor Flotante en QLineEdit")
        self.show()

    def process_value(self):
        try:
            # Obtener el texto del QLineEdit y convertirlo a un número flotante
            coord_z_value = float(self.coord_z_line_edit.text())
            
            # Hacer algo con el valor flotante, por ejemplo, imprimir en la consola
            print("Valor flotante ingresado:", coord_z_value)
            
        except ValueError:
            # Manejar el caso en el que el texto no sea un número flotante válido
            print("Error: Ingrese un valor flotante válido.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = MyWidget()
    sys.exit(app.exec_())

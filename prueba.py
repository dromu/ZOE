from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSlider, QLabel
from PyQt5.QtCore import Qt
import sys

class MiVentana(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.slider = QSlider(Qt.Horizontal)

        valores_fijos = [0, 25, 50, 75, 100]

        self.slider.setRange(0, len(valores_fijos) - 1)
        self.slider.setTickInterval(1)
        self.slider.setTickPosition(QSlider.TicksBelow)

        self.slider.sliderPressed.connect(self.incrementar_valor_fijo)
        self.slider.valueChanged.connect(self.actualizar_label)

        layout.addWidget(self.slider)

        self.label_valor = QLabel()
        layout.addWidget(self.label_valor)

        self.setLayout(layout)
        self.setWindowTitle('QSlider con Valores Fijos')
        self.show()

    def incrementar_valor_fijo(self):
        # Aumentar el valor fijo al hacer clic en el QSlider
        valor_actual = self.slider.value()
        self.slider.setValue(min(valor_actual + 1, self.slider.maximum()))

    def actualizar_label(self, indice):
        valores_fijos = [0, 25, 50, 75, 100]
        valor_seleccionado = valores_fijos[indice]
        self.label_valor.setText(f"Valor seleccionado: {valor_seleccionado}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = MiVentana()
    sys.exit(app.exec_())

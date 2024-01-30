import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton
from PyQt5.QtGui import QIntValidator


class MyWidget(QWidget):
    def __init__(self):
        super(MyWidget, self).__init__()

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        self.line_edit = QLineEdit(self)
        self.line_edit.setValidator(QIntValidator(0, 100, self))  # Establecer un validador para permitir solo números de 0 a 100
        self.layout.addWidget(self.line_edit)

        self.btn_increase = QPushButton('Aumentar', self)
        self.btn_increase.clicked.connect(self.increase_value)
        self.layout.addWidget(self.btn_increase)

        self.btn_decrease = QPushButton('Disminuir', self)
        self.btn_decrease.clicked.connect(self.decrease_value)
        self.layout.addWidget(self.btn_decrease)

        self.setLayout(self.layout)

    def increase_value(self):
        current_value = int(self.line_edit.text())
        if current_value < 100:
            self.line_edit.setText(str(current_value + 1))

    def decrease_value(self):
        current_value = int(self.line_edit.text())
        if current_value > 0:
            self.line_edit.setText(str(current_value - 1))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_widget = MyWidget()
    my_widget.show()
    sys.exit(app.exec_())

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QColorDialog, QSlider
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen
from PyQt5.QtCore import Qt

class DrawingWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.label = QLabel(self)
        self.pixmap = QPixmap(400, 400)
        self.pixmap.fill(Qt.white)
        self.label.setPixmap(self.pixmap)

        self.pen_color = Qt.black
        self.pen_size = 2

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Controles para seleccionar el color y tamaño del trazo
        color_button = QPushButton("Seleccionar color", self)
        color_button.clicked.connect(self.select_color)
        layout.addWidget(color_button)

        size_slider = QSlider(Qt.Horizontal)
        size_slider.setRange(1, 20)
        size_slider.setValue(self.pen_size)
        size_slider.valueChanged.connect(self.set_pen_size)
        layout.addWidget(size_slider)

        layout.addWidget(self.label)

        self.last_pos = None

    def select_color(self):
        color = QColorDialog.getColor(self.pen_color, self, "Seleccionar color de trazo")
        if color.isValid():
            self.pen_color = color

    def set_pen_size(self, size):
        self.pen_size = size

    def paintEvent(self, event):
        painter = QPainter(self.label.pixmap())
        painter.setPen(QPen(self.pen_color, self.pen_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        if self.last_pos:
            painter.drawLine(self.last_pos, self.end_pos)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_pos = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() and Qt.LeftButton:
            self.end_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_pos = None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QWidget()
    drawing_widget = DrawingWidget()
    window.setLayout(QVBoxLayout())
    window.layout().addWidget(drawing_widget)
    window.show()
    sys.exit(app.exec_())

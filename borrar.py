import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt5.QtGui import QPixmap, QPainter, QPen
from PyQt5.QtCore import Qt, QPoint

class DrawingWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.pixmap = QPixmap(400, 300)
        self.pixmap.fill(Qt.white)
        self.last_point = QPoint()
        self.end_point = QPoint()  # Initialize end_point here

        self.init_ui()

    def init_ui(self):
        self.label = QLabel(self)
        self.label.setPixmap(self.pixmap)

    def paintEvent(self, event):
        painter = QPainter(self.pixmap)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(QPen(Qt.black, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

        painter.drawLine(self.last_point, self.end_point)

        self.label.setPixmap(self.pixmap)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_point = event.pos()
            self.end_point = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() and Qt.LeftButton:
            self.end_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.end_point = event.pos()
            self.update()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QWidget()
    drawing_widget = DrawingWidget()

    layout = QVBoxLayout(window)
    layout.addWidget(drawing_widget)

    window.setGeometry(100, 100, 400, 300)
    window.show()

    sys.exit(app.exec_())

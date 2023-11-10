import sys
from PyQt5 import uic, QtWidgets
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QPoint
from img_tools.CameraView import ProcesadorCamara
from PyQt5.QtWidgets import QFileDialog
from img_tools.DrawingBoard import DrawingBoard

class MyApp(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ui_file = "gui\zoe_main.ui"
        Ui_MainWindow, QtBaseClass = uic.loadUiType(ui_file)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        #Crea un objeto y llamada un metodo de la otra clase
        self.ui.tablero = DrawingBoard(self.ui.tablero)
        self.ui.pbDot.clicked.connect(self.ui.tablero.habEscritura)
        self.ui.pbTrash.clicked.connect(self.ui.tablero.clear)

        self.ui.procesador_camara = ProcesadorCamara()
        self.ui.procesador_camara.iniciar_camara()
        self.ui.procesador_camara.senal_actualizacion.connect(self.actualizar_interfaz)

        # self.ui.brushColor = Qt.black
        self.ui.blueAction.triggered.connect(lambda: self.ui.tablero.pincelColor("blue"))
        self.ui.redAction.triggered.connect(lambda: self.ui.tablero.pincelColor("red"))
        self.ui.greenAction.triggered.connect(lambda: self.ui.tablero.pincelColor("green"))
        self.ui.blackAction.triggered.connect(lambda: self.ui.tablero.pincelColor("black"))
        self.ui.yellowAction.triggered.connect(lambda: self.ui.tablero.pincelColor("yellow"))
        self.ui.whiteAction.triggered.connect(lambda: self.ui.tablero.pincelColor("white"))

        self.ui.onepxAction.triggered.connect(lambda: self.ui.tablero.pincelSize(1))
        self.ui.threepxAction.triggered.connect(lambda: self.ui.tablero.pincelSize(3))
        self.ui.fivepxAction.triggered.connect(lambda: self.ui.tablero.pincelSize(5))
        self.ui.sevenpxAction.triggered.connect(lambda: self.ui.tablero.pincelSize(7))
        self.ui.ninepxAction.triggered.connect(lambda: self.ui.tablero.pincelSize(9))

        self.ui.pbSave.clicked.connect(self.save)

    def actualizar_interfaz(self, frame):
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        self.ui.pixmap = QPixmap.fromImage(q_image)
        self.ui.cameraSpace.setPixmap(self.ui.pixmap)

    def save(self):
        combined_image = QImage(self.ui.tablero.size(), QImage.Format_ARGB32)
        combined_image.fill(Qt.transparent)
        painter = QPainter(combined_image)
        painter.drawPixmap(0, 0, self.ui.pixmap)
        painter.drawPixmap(0, 0, self.ui.tablero.pixmap_tablero)
        painter.end()

        filePath, _ = QFileDialog.getSaveFileName(self, "Guardar imagen", "", "PNG(*.png);;JPEG(*.jpg *.jpeg);; All Files(*.)")
        if filePath == "":
            return

        combined_image.save(filePath)

   
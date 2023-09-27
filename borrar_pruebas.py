import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QMenu, QMenuBar
from PyQt5.QtMultimedia import QCameraInfo

class CameraMenuApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.camera_menu = QMenu("Cámara", self)
        self.populate_camera_menu()

        menubar = self.menuBar()
        menubar.addMenu(self.camera_menu)

        self.setWindowTitle("Menú de Cámara")
        self.setGeometry(100, 100, 300, 200)

    def populate_camera_menu(self):
        available_cameras = QCameraInfo.availableCameras()

        self.camera_menu.clear()

        for camera_info in available_cameras:
            camera_name = camera_info.description()
            action = QAction(camera_name, self)
            action.triggered.connect(lambda checked, camera_info=camera_info: self.on_camera_selected(camera_info))
            self.camera_menu.addAction(action)

    def on_camera_selected(self, camera_info):
        print(f"Cámara seleccionada: {camera_info.description()}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CameraMenuApp()
    window.show()
    sys.exit(app.exec_())

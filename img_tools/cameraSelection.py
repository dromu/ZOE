import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QComboBox, QPushButton
from PyQt5.QtMultimedia import QCameraInfo

class DialogoSeleccionCamara(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Seleccionar Cámara")
        self.setGeometry(200, 200, 300, 150)

        layout = QVBoxLayout()

        # Combo box para mostrar las cámaras disponibles
        self.combo_cameras = QComboBox()
        self.actualizar_lista_camaras()
        layout.addWidget(self.combo_cameras)

        # Botones para aceptar o cancelar la selección
        self.btn_aceptar = QPushButton("Aceptar")
        self.btn_aceptar.clicked.connect(self.aceptar_seleccion)
        layout.addWidget(self.btn_aceptar)

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.clicked.connect(self.close)
        layout.addWidget(self.btn_cancelar)

        self.setLayout(layout)

    def actualizar_lista_camaras(self):
        # Limpiar el combo box antes de actualizar la lista de cámaras
        self.combo_cameras.clear()

        # Obtener la lista de cámaras disponibles
        cameras = QCameraInfo.availableCameras()
        
        for camera in cameras:
            self.combo_cameras.addItem(camera.description())

    def aceptar_seleccion(self):
        # Obtener la cámara seleccionada
        indice_seleccionado = self.combo_cameras.currentIndex()
        camera_info = QCameraInfo.availableCameras()[indice_seleccionado]
        camera_name = camera_info.deviceName()
        camera_description = camera_info.description()

        dataCamera = str(indice_seleccionado)+str(camera_name)
        
        print(f"Cámara seleccionada: {camera_name} - {camera_name}")

        # Aquí puedes realizar alguna acción con la cámara seleccionada, como abrir una ventana de vista previa, etc.
        # Por ahora, solo imprimimos la información de la cámara seleccionada.
        self.guardar_variable(dataCamera,"img_tools/camera.dat" )
        self.close()

    def guardar_variable(self,variable,archivo):

        with open(archivo, 'w') as archivo:
            archivo.write(variable)
        
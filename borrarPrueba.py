import os
from PyQt5.QtWidgets import QApplication, QFileDialog

app = QApplication([])

options = QFileDialog.Options()
options |= QFileDialog.DontUseNativeDialog

file_name, selected_filter = QFileDialog.getSaveFileName(None, "Guardar como", "", "Imágenes (*.jpg);;Todos los archivos (*)", options=options)

if file_name:
    _, file_extension = os.path.splitext(file_name)
    print("Archivo seleccionado:", file_name)
    print("Extensión seleccionada:", file_extension)
else:
    print("No se seleccionó ningún archivo.")

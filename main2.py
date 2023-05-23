import sys
from PyQt5 import uic, QtWidgets
import pywifi
from pywifi import const
import time

qtCreatorFile = "zoe_main.ui"  # Nombre del archivo aquí.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.BuConnect.setStyleSheet("QPushButton { background-color: red;  }")
        self.BuConnect.clicked.connect(self.conexion)
        self.is_connected = False

    def conexion(self):
        if self.is_connected:
            self.disconnect_wifi()

        else:
            self.connect_to_wifi()
            
        self.is_connected = not self.is_connected

    def connect_to_wifi(self):
        ssid = "MiRedWiFi"
        password = "mi_contrasena"
        wifi = pywifi.PyWiFi()  # Inicializa la biblioteca pywifi
        iface = wifi.interfaces()[0]  # Obtiene la primera interfaz WiFi
        iface.disconnect()  # Desconecta de cualquier red WiFi actual
        profile = pywifi.Profile()  # Crea un nuevo perfil de red WiFi
        profile.ssid = ssid  # Establece el SSID de la red WiFi
        profile.auth = const.AUTH_ALG_OPEN  # Establece el tipo de autenticación (abierta)
        profile.akm.append(const.AKM_TYPE_WPA2PSK)  # Establece el tipo de cifrado (WPA2-PSK)
        profile.cipher = const.CIPHER_TYPE_CCMP  # Establece el tipo de cifrado (CCMP)
        profile.key = password  # Establece la contraseña de la red WiFi
        tmp_profile = iface.add_network_profile(profile)  # Agrega el perfil de red WiFi
        iface.connect(tmp_profile)  # Conéctate a la red WiFi

        time.sleep(2)

        if iface.status() == const.IFACE_CONNECTED:  # Verifica si se ha establecido la conexión
            print("Conexión establecida.")
            self.BuConnect.setText('Conectado')
            self.BuConnect.setStyleSheet("QPushButton { background-color: green; }")
        else:
            print("No se pudo establecer la conexión.")

    def disconnect_wifi(self):
        wifi = pywifi.PyWiFi()  # Inicializa la biblioteca pywifi
        iface = wifi.interfaces()[0]  # Obtiene la primera interfaz WiFi

        iface.disconnect()  # Desconecta de la red WiFi actual

        if iface.status() == pywifi.const.IFACE_DISCONNECTED:  # Verifica si se ha desconectado correctamente
            print("Desconexión exitosa.")

            self.BuConnect.setText('Conectar')
            self.BuConnect.setStyleSheet("QPushButton { background-color: red; }")
        else:
            print("No se pudo desconectar.")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())

import pywifi
from pywifi import const
import time 

class WifiConnector:
    def __init__(self):
        self.is_connected = False
        self.wifi = pywifi.PyWiFi()  # Inicializa la biblioteca pywifi
        self.iface = self.wifi.interfaces()[0]  # Obtiene la primera interfaz WiFi
        
    def connect(self):
        ssid = "ZOE"
        password = "0123456789"
        self.iface.disconnect()  # Desconecta de cualquier red WiFi actual
        profile = pywifi.Profile()  # Crea un nuevo perfil de red WiFi
        profile.ssid = ssid  # Establece el SSID de la red WiFi
        profile.auth = const.AUTH_ALG_OPEN  # Establece el tipo de autenticación (abierta)
        profile.akm.append(const.AKM_TYPE_WPA2PSK)  # Establece el tipo de cifrado (WPA2-PSK)
        profile.cipher = const.CIPHER_TYPE_CCMP  # Establece el tipo de cifrado (CCMP)
        profile.key = password  # Establece la contraseña de la red WiFi
        tmp_profile = self.iface.add_network_profile(profile)  # Agrega el perfil de red WiFi
        self.iface.connect(tmp_profile)  # Conéctate a la red WiFi

        time.sleep(2)

        if self.iface.status() == const.IFACE_CONNECTED:  # Verifica si se ha establecido la conexión
            print("Conexión establecida.")
            self.is_connected = True
            
        else:
            print("No se pudo establecer la conexión.")
            self.is_connected = False
        
        return self.is_connected
   
        
    def disconnect(self):
        self.iface.disconnect()  # Desconecta de la red WiFi actual

        if self.iface.status() == pywifi.const.IFACE_DISCONNECTED:  # Verifica si se ha desconectado correctamente
            print("Desconexión exitosa.")
            self.is_connected = False
        else:
            print("No se pudo desconectar.")
            self.is_connected = True

        return self.is_connected
    
    def ver_connected(self, ssid):
        current_ssid = self.iface.ssid()  # Obtiene el SSID de la red WiFi actual
        return current_ssid == ssid
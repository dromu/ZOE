import pywifi
from pywifi import const
import time 
from comunication.TCP_comunication import TCP_comunication

class WifiConnector:
    def __init__(self):
        """
        El código anterior define una clase con métodos para conectarse a una red WiFi, desconectarse de
        una red WiFi y verificar si el dispositivo está actualmente conectado a una red WiFi específica.
        """
        self.is_connected = False
        self.wifi = pywifi.PyWiFi()  # Inicializa la biblioteca pywifi
        self.iface = self.wifi.interfaces()[0]  # Obtiene la primera interfaz WiFi
        
        self.sendData = TCP_comunication()

    def connect(self):

        self.olvidarRed()
        """
        La función se conecta a una red WiFi utilizando el SSID y la contraseña proporcionados.
        
        Returns:
        Retorna un valor booleano que indica si la conexión a la red WiFi fue exitosa o no. Si se establece la conexión, devuelve Verdadero. De lo contrario, devuelve Falso.
        """
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
            self.is_connected = True
            
        else:
            self.is_connected = False
        
        return self.is_connected
   
        
    def disconnect(self):
        """
        La función se desconecta de la red WiFi actual y devuelve un booleano que indica si la desconexión
        fue exitosa o no.
        
        Returns:
          El método devuelve el valor de la variable "self.is_connected".
        """
        

        self.iface.disconnect()  # Desconecta de la red WiFi actual

        if self.iface.status() == pywifi.const.IFACE_DISCONNECTED:  # Verifica si se ha desconectado correctamente
            print("Desconexión exitosa.")
            self.is_connected = False
            self.olvidarRed()
        else:
            print("No se pudo desconectar.")
            self.is_connected = True

        return self.is_connected
    
    def ver_connected(self, ssid):
        """
        La función "ver_connected" comprueba si el SSID de la red WiFi actual coincide con el SSID
        proporcionado.
        
        Args:
          ssid: El parámetro `ssid` es una cadena que representa el SSID (Identificador de conjunto de
        servicios) de una red WiFi.
        
        Returns:
          un valor booleano que indica si el SSID actual de la red WiFi es igual al SSID proporcionado.
        """
        current_ssid = self.iface.ssid()  # Obtiene el SSID de la red WiFi actual
        return current_ssid == ssid
    
    def olvidarRed(self):

        if self.iface.status() == pywifi.const.IFACE_DISCONNECTED:  # Verifica si se ha desconectado correctamente
            print("Desconexión exitosa.")
            self.is_connected = False

            perfiles = self.iface.network_profiles()

            for perfil in perfiles:
                if perfil.ssid == 'ZOE':
                    self.iface.remove_network_profile(perfil)
                    print('Red "ZOE" olvidada correctamente.')
                    break
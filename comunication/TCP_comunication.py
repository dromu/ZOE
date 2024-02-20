import socket

# La clase `TCP_comunication` es una clase de Python que maneja la comunicación TCP conectándose a una
# dirección y puerto específicos, enviando datos y cerrando la conexión.

class TCP_comunication: 
    def __init__(self):
        """
        La función inicializa los valores de la dirección IP, el puerto y las variables del cliente.
        """
        self.addres = "192.168.4.1"
        self.port   = 8080
        self.cliente = None

        self.flag = False
        

    def connect(self):
        """
        La función se conecta a un servidor mediante un socket TCP.
        """
        self.cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cliente.connect((self.addres, self.port)) 

        
    def send(self, datos):
        """
        La función envía los datos codificados al cliente.
        
        Args:
          datos: El parámetro "datos" es una cadena que representa los datos que desea enviar. Se
        codificará utilizando la codificación UTF-8 antes de enviarlo a través del socket del cliente.
        """
        # self.cliente.sendall(datos.encode('utf-8'))

        try:
            self.cliente.sendall(datos.encode('utf-8'))
            print("Datos enviados exitosamente.")
            return False
        except socket.error:
            print("Error al enviar datos.")
            return True
 

    def close(self):
        """
        La función de cierre cierra la conexión del cliente si existe.
        """
        
        if self.cliente:
            print("Desconectando del socket")
            self.cliente.close()
            self.cliente = None
            self.flag = True
            return True
        else:
            
            return False
    
    def check_connection(self):
        """
        Verifica si hay una conexión activa.
        """
        if self.client:
            return True
        else:
            return False
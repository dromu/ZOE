import socket

class TCP_comunication: 
    def __init__(self):
        self.addres = "192.168.4.1"
        self.port   = 8080
        self.cliente = None
        

    def connect(self):
        self.cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cliente.connect((self.addres, self.port)) 

        
    def send(self, datos):
       self.cliente.sendall(datos.encode('utf-8'))

       # Esperar la respuesta del servidor
       #self.respuesta = self.cliente.recv(1024)
       #print(f"Respuesta del servidor: {self.respuesta.decode('utf-8')}")

    def close(self):
        if self.cliente:
            self.cliente.close()
            self.cliente = None

# if __name__ == "__main__":
#     dato = TCP_comunication()
#     dato.send("holi")

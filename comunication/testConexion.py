import socket

class ESP32Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        if self.sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(10)
            try:
                self.sock.connect((self.host, self.port))
                print("Conectado al ESP32")
            except socket.error as e:
                print(f"Error al conectar: {e}")
                self.sock = None

    def disconnect(self):
        if self.sock is not None:
            self.sock.close()
            self.sock = None
            print("Desconectado del ESP32")

    def send_receive(self, message):
        if self.sock is not None:
            try:
                self.sock.sendall(message.encode())
                response = self.sock.recv(1024)
                return response.decode()
            except socket.error as e:
                print(f"Error al enviar/recibir datos: {e}")
        else:
            print("No está conectado al ESP32")
        return None
    
    def receive_message(self):
        if self.sock is not None:
            try:
                response = self.sock.recv(128) 
                return response.decode()
            except socket.error as e:
                print(f"Error al recibir datos: {e}")
        else:
            print("No está conectado al ESP32")
        return None

# Ejemplo de uso
# if __name__ == "__main__":
#     client = ESP32Client('192.168.4.1', 80)
    
#     client.connect()
    
#     response = client.send_receive("Hola ESP32")
#     if response:
#         print("Respuesta del ESP32:", response)
    
#     client.disconnect()

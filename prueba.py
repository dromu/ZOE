import cv2

def listar_camaras():
    # Obtener la lista de dispositivos de captura disponibles
    dispositivos = [f"Camara {i}" for i in range(10) if cv2.VideoCapture(i).isOpened()]

    # Imprimir la lista de cámaras
    if dispositivos:
        print("Cámaras disponibles:")
        for camara in dispositivos:
            print(camara)
    else:
        print("No se encontraron cámaras disponibles.")

if __name__ == "__main__":
    listar_camaras()

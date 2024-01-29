def readCamera():
    with open("img_tools\camera.dat", 'r') as archivo:
        contenido = archivo.read()
    
    if contenido[0] == None:
        return 0 
    else: 
        return int(contenido[0])

print(readCamera())
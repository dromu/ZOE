from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu,QAction,QFileDialog
from PyQt5.QtGui import QIcon, QImage, QPainter, QPen, QPolygon
from PyQt5.QtCore import Qt, QPoint, QRect
import sys


#hereda la clase QMainWindows
class Window(QMainWindow):
    #Constructor
    def __init__(self):
        # Hereda todos los atributos y metodos de la clase padre 
        super().__init__()

        top     = 400
        left    = 400
        width   = 800
        height  = 600
        # icon    =  
        
        self.begin, self.destination = QPoint(), QPoint()	
    
        self.setWindowTitle("Paint Application")        # Nombre que aparece en Ventana
        self.setGeometry(top,left,width,height)         # Tamaño ventana
        # self.setWindowIcon(icon)                      # Agrega un icono 

        self.image  =   QImage(self.size(), QImage.Format_RGB32)
        self.image.fill(Qt.white)

        # PArametros por defecto para iniciar la pintura
        self.drawing    = False         # Desactivado para no iniciar a dibujar 
        self.brushSize  = 5
        self.brushColor = Qt.black

        self.lastPoint  = QPoint()
        
        #se crea un objeto de menubar
        mainMenu    =   self.menuBar()
        fileMenu    =   mainMenu.addMenu("File")
        brushMenu   =   mainMenu.addMenu("Brush Size")
        brushColor  =   mainMenu.addMenu("Brush Color")
        poligon     =   mainMenu.addMenu("Poligon")

        # Acciones del Boton file 
        saveAction = QAction("Save", self)
        saveAction.setShortcut("Ctrl+S")
        fileMenu.addAction(saveAction)
        saveAction.triggered.connect(self.save)

        clearAction = QAction("Clear", self)
        clearAction.setShortcut("Ctrl+L")
        fileMenu.addAction(clearAction)
        clearAction.triggered.connect(self.clear)

        # Acciones del Boton brushMenu
        threepxAction = QAction("3px", self)
        brushMenu.addAction(threepxAction)
        threepxAction.triggered.connect(self.threepx)

        fivepxAction = QAction("5px", self)
        brushMenu.addAction(fivepxAction)
        fivepxAction.triggered.connect(self.fivepx)

        sevenpxAction = QAction("7px", self)
        brushMenu.addAction(sevenpxAction)
        sevenpxAction.triggered.connect(self.sevenpx)

        ninepxAction = QAction("9px", self)
        brushMenu.addAction(ninepxAction)
        ninepxAction.triggered.connect(self.ninepx)

        # Acciones del Boton brushColor
        blackAction =   QAction("Black",self)
        brushColor.addAction(blackAction)
        blackAction.triggered.connect(self.brushBlack)

        redAction =   QAction("Red",self)
        brushColor.addAction(redAction)
        redAction.triggered.connect(self.brushRed)

        blueAction =   QAction("Blue",self)
        brushColor.addAction(blueAction)
        blueAction.triggered.connect(self.brushBlue)

        greenAction =   QAction("Green",self)
        brushColor.addAction(greenAction)
        greenAction.triggered.connect(self.brushGreen)

        yellowAction =   QAction("Yellow",self)
        brushColor.addAction(yellowAction)
        yellowAction.triggered.connect(self.brushYellow)

        # Acciones del Boton poligon

        rectangleAction = QAction("Rectangle", self)
        poligon.addAction(rectangleAction)
        rectangleAction.triggered.connect(self.polRectangle)

        self.flag = False

    def mousePressEvent(self, event):

        #Cuando da click activa el evento cuando se presiona un click
        if event.button() == Qt.LeftButton:         #Click izquierdo
            # self.drawing        = True              #Habilita el dibujo
            # self.lastPoint      = event.pos()       #Toma la ultima posicion 

            #Inicia la pintura sobre el lienzo
            painter = QPainter(self.image)

            #Configura el tipo de pincel
            painter.setPen(QPen(self.brushColor, self.brushSize, Qt.SolidLine,Qt.RoundCap, Qt.RoundJoin)) 
            

            # Graba la posicion inicial
            self.begin = event.pos()
            print("self.begin: ",self.begin)

            # Actualiza el punto final pero como solo existe una posicion toma el mismo 
            self.destination = self.begin
            self.update()

    #Eventos cuando se mueve el mouse 
    def mouseMoveEvent(self, event): 
        if (event.buttons() & Qt.LeftButton):
            painter = QPainter(self.image)
            print('Point 2')	
            #Graba la posicion donde se mueve el mouse
            self.puntoAnte = self.destination
            self.destination = event.pos()
            print("self.destination: ", self.destination)

            painter.drawLine(self.puntoAnte, self.destination)

            #Actualiza todo el espacio 
            self.update()

    def mouseReleaseEvent(self, event):
        if (event.button() & Qt.LeftButton):
            
            #SE crea un objeto rectangular que recibe la posicion inicial y final 
            rect    = QRect(self.begin, self.destination)
            
            #Objeto para empezar a pintar 
            painter = QPainter(self.image)

            # Pinta el rectangulo 
            painter.drawRect(rect.normalized())

            # painter.drawLine(self.begin, event.pos())

            print("mouseReleaseEvent")
            



    def paintEvent(self,event):
        canvasPainter   =  QPainter(self)
        canvasPainter.drawImage(self.rect(), self.image, self.image.rect())
        

        if not self.begin.isNull() and not self.destination.isNull():
            rect = QRect(self.begin, self.destination)
            canvasPainter.drawRect(rect.normalized())
            print("paintEvent")
   
          


        

            
            
            

    def save(self):
        filePath, _ = QFileDialog.getSaveFileName(self,"Save Image","", "PNG(*.png);;JPEG(*.jpg *.jpeg);; All Files(*.)")
        if filePath == "":
            return
        self.image.save(filePath)
    
    def clear(self):
        self.image.fill(Qt.white)       #Vuelve pantalla a blanco
        self.update()                   #Actualiza todo para limpie pantalla
    
    #Tamaños de pincel
    def threepx(self):
        self.brushSize = 3
    def fivepx(self):
        self.brushSize = 5
    def sevenpx(self):
        self.brushSize = 7
    def ninepx(self):
        self.brushSize = 9

    #Colores 
    def brushBlack(self):
        self.brushColor = Qt.black
    def brushRed(self):
        self.brushColor = Qt.red
    def brushBlue(self):
        self.brushColor = Qt.blue
    def brushGreen(self):
        self.brushColor = Qt.green
    def brushYellow(self):
        self.brushColor = Qt.yellow

    # Poligonos
    def polRectangle(self):
        self.flag = True


    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()       # llamamos el objetov
    window.show()           # Mostramos 
    app.exec()                  
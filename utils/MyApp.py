import sys
from PyQt5 import uic, QtWidgets
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QPoint
from img_tools.CameraView import ProcesadorCamara
from PyQt5.QtWidgets import QFileDialog, QActionGroup

from img_tools.DrawingBoard import DrawingBoard
from comunication.TCP_comunication import TCP_comunication
from comunication.wificonnector import WifiConnector



class MyApp(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ui_file = "gui\zoe_main.ui"
        Ui_MainWindow, QtBaseClass = uic.loadUiType(ui_file)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


        #Color complementario 
        # self.ui.colorComp = complementaryColor(self.ui.tablero)
        

        #Crea un objeto y llamada un metodo de la clase DrawingBoard

        #Botones de dibujo
        self.ui.tablero = DrawingBoard(self.ui.tablero)                 # Objeto
        self.ui.pbDot.clicked.connect(self.ui.tablero.habEscritura)     # Dibujo libre
        self.ui.pbRect.clicked.connect(self.ui.tablero.habRect)         # Rectangulos 
        self.ui.pbHide.clicked.connect(self.ui.tablero.hideWind)        # Ocultar cambios
        self.ui.pbTrash.clicked.connect(self.ui.tablero.clear)          # Limpiar pantalla
        self.ui.pbElip.clicked.connect(self.ui.tablero.habElipse)       # Boton de generar elipses
        self.ui.pbText.clicked.connect(self.ui.tablero.habText)         # Texto
        self.ui.pbDel.clicked.connect(self.ui.tablero.habDel)           # Eliminacion de escrito
        self.ui.pbROI.clicked.connect(self.ui.tablero.habColor)         # Generacion de color complementario
        # self.ui.pbArrow.clicked.connect(self.ui.tablero.habArrow)

        
        # Union a metodos locales de la clase para cambio de color 
        self.ui.pbDot.clicked.connect(self.habEscritura)
        self.ui.pbROI.clicked.connect(self.habColor)


        # Valores iniciales de las variables
        self.flagEscritura = False
        self.flagColor = False
        self.visCamera = False

        # Imagen de inicio de en lugar de visualizacion de muestras 
        self.img_pixmap = QPixmap("images\microscopio.png")
        self.ui.cameraSpace.setPixmap(self.img_pixmap)

        # Objetos para envio de informacion 
        self.connector = WifiConnector()
        self.send_data = TCP_comunication()
        self.ui.procesador_camara = ProcesadorCamara()
        
 

        # Conexion de las herramientas de la barra de tareas 
        color_actions = {
            self.ui.blueAction: "blue",
            self.ui.redAction: "red",
            self.ui.greenAction: "green",
            self.ui.blackAction: "black",
            self.ui.yellowAction: "yellow",
            self.ui.whiteAction: "white",
        }
        

        for action, color in color_actions.items():
            action.triggered.connect(lambda _, c=color: self.ui.tablero.pincelColor(c))

        # Conexion del tamaño del pincel
        # sizes = ["one", "three", "five", "seven", "nine"]
        # for size in sizes:
        #     action = getattr(self.ui, f"{size}pxAction")
        #     action.triggered.connect(lambda s=size: self.ui.tablero.pincelSize(s))

                # Suponiendo que sizes es una lista de tamaños de pincel
        sizes = ["one", "three", "five", "seven", "nine"]

        # Conecta las acciones de tamaño del pincel al método común dentro de un grupo de acciones
        grupo_tamanos_pincel = QActionGroup(self)
        for size in sizes:
            action = getattr(self.ui, f"{size}pxAction")
            action.setCheckable(True)
            grupo_tamanos_pincel.addAction(action)
            action.triggered.connect(lambda checked, s=size: self.ui.tablero.pincelSize(s))


        #Boton de guardar pantallas 
        self.ui.pbSave.clicked.connect(self.save)

        
        ## Elementos en el main 
        # Boton de inicio de conexion
        self.ui.pbConnect.clicked.connect(self.conexion)
        #Texto inicial de conexion 
        self.ui.txtConnect.setText("No conectado")
        # Slider de espectro visible
        self.ui.VisibleEsp.valueChanged.connect(self.slider_value_changed)
        
        # Se crea un objeto connector
        self.connector = WifiConnector()

        #Obejto envio
        self.send_data = TCP_comunication()
        
        # Deshabilitamos los elementos del main, estos se irán actualizando
        self.ui.wavelength.setEnabled(False)
        self.ui.VisibleEsp.setEnabled(False)
        self.ui.RB_manual.setEnabled(False)
        self.ui.RB_auto.setEnabled(False)
        self.ui.RB_white.setEnabled(False)

        # Cambiar el valor del slider en texto
        self.ui.wavelength.returnPressed.connect(self.line_edit_return_pressed)

        # Seleccion de modo luz blanca por defecto
        self.ui.RB_white.setChecked(True)

        # Conectar todos los botones de radio a la función processRadioButton
        buttons = [self.ui.RB_manual, self.ui.RB_auto, self.ui.RB_white]
        for button in buttons:
            button.toggled.connect(lambda state, b=button: self.processRadioButton(b, self.ui.VisibleEsp, self.ui.wavelength))

        self.ui.value = 380
        
        

        self.manejoButton(False)

        
    
    def manejoButton(self, condicion): 
        buttonName = ("pbDot","pbRect","pbHide","pbTrash", "pbElip", "pbText", "pbDel", "pbROI", "pbSave", "pbArrow", "pbBack", "pbForw")

        if condicion:
            for key in buttonName:
                button = getattr(self.ui, key, None)
                if button:
                    button.setEnabled(condicion)

        else:
            for key in buttonName:
                button = getattr(self.ui, key, None)
                if button:
                    button.setEnabled(condicion)
    
    def deactivateButton(self):
        self.ui.tablero.habEscritura()
        self.habEscritura()
        

    def habEscritura(self):
        self.flagEscritura = not self.flagEscritura

        color = "red" if self.flagEscritura else "white"
        self.ui.pbDot.setStyleSheet(f"QPushButton {{ background-color: {color}; }}")

    
    def habColor(self):
        #entra con el segundo click
        self.flagColor = not self.flagColor

        if self.flagColor == False:
            self.ui.RB_auto.setChecked(True)
            # Al presionar dos veces se comprueba el color complementario 
            R_,G_,B_ = self.ui.procesador_camara.colorComplementary()

            dato  = str(R_)+str(G_)+str(B_)

            print(R_, G_, B_ )
        
        

    def actualizar_interfaz(self, frame):
        if self.visCamera:
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            self.ui.pixmap = QPixmap.fromImage(q_image)
            self.ui.cameraSpace.setPixmap(self.ui.pixmap)
        
        else: 
            #Coloca una imagen sino no actualiza

            self.ui.cameraSpace.setPixmap(self.img_pixmap)



    def save(self):
        combined_image = QImage(self.ui.tablero.size(), QImage.Format_ARGB32)
        combined_image.fill(Qt.transparent)
        painter = QPainter(combined_image)
        painter.drawPixmap(0, 0, self.ui.pixmap)
        painter.drawPixmap(0, 0, self.ui.tablero.pixmap_tablero)
        painter.end()

        filePath, _ = QFileDialog.getSaveFileName(self, "Guardar imagen", "", "PNG(*.png);;JPEG(*.jpg *.jpeg);; All Files(*.)")
        if filePath == "":
            return

        combined_image.save(filePath)

    def processRadioButton(self, radio_button, slider, wavelength):
        if radio_button.isChecked():

            print(radio_button.text())
            
            if radio_button.text() == 'Manual':
                # Se habilitan todas las modificaciones al espectro 
                slider.setEnabled(True)    
                wavelength.setEnabled(True)    
                
                
            if radio_button.text() == 'Automático':
                ##self.ui.value = 500
                self.send_data.send("A"+str(self.ui.value)+   "000000" )  

                # self.ui.send_data.send(str(self.ui.value) )  

                # ACtualizamos el valor directamente, con el obtenido del cambio de espacio 
                self.ui.wavelength.setText(str(self.ui.value))

                # Se limitan las acciones para que no se pueda mover la longitud
                self.ui.wavelength.setEnabled(False)
                self.ui.VisibleEsp.setEnabled(False)
               
            if radio_button.text() == 'Luz blanca':
                # Se limitan y paran todas las acciones 
                self.send_data.send("W"+str(self.ui.value)+  "000000" ) 
                self.ui.wavelength.setEnabled(False)
                self.ui.VisibleEsp.setEnabled(False)
                
            slider.setValue(self.ui.value)
           
    # Recibe los valores de cambio del slider
    def slider_value_changed(self, value):
        # Checkea el boton manual
        if self.ui.RB_manual.isChecked():
            self.ui.wavelength.setText(str(value))
            self.ui.value = int(value) # ACtualizamos el valor para que la barra quede en el mismo punto del manual
            print(str(value))
            self.send_data.send("M" + str(value) +  "000000" )  
        else:
            # Se deshabilita cualquier accion diferente
            self.ui.wavelength.setEnabled(False)
            self.ui.VisibleEsp.setEnabled(False)

    # Hace referencia al recuadro para cambio de longitud
    def line_edit_return_pressed(self):
        value = self.ui.wavelength.text()
        if value.isdigit():
            value = int(self.ui.wavelength.text())
            if 380 <= value <= 780:
                self.ui.VisibleEsp.setValue(value)
            else:
                self.ui.wavelength.setText("Invalid value!")
        else:
                self.ui.wavelength.setText("Invalid value!")

    # Proceso de conexion del pc-esp32
    def conexion(self):
        if self.connector.is_connected:     #Revisa el atributo en el constructor

            
            if not self.connector.disconnect(): #Revisa los retornos de los metodos 
                self.ui.pbConnect.setText('Conectar')
                self.ui.pbConnect.setStyleSheet("QPushButton { background-color: red; }")
                self.ui.txtConnect.setText("Desconexión exitosa")

                self.ui.RB_manual.setEnabled(False)
                self.ui.RB_auto.setEnabled(False)
                self.ui.RB_white.setEnabled(False)
                self.ui.wavelength.setEnabled(False)
                self.ui.VisibleEsp.setEnabled(False)

                self.visCamera = False

               # Desactivamos botones 
                self.manejoButton(False)

                # Limpiar la pantalla  para vovler a la imagen inicial
                self.ui.tablero.clear()

                # Desactivacion de todos los botones 
                self.deactivateButton()


            else:
                self.ui.txtConnect.setText("No se pudo desconectar.")

        else:
            if self.connector.connect():
                self.ui.pbConnect.setText('Conectado')
                self.ui.pbConnect.setStyleSheet("QPushButton { background-color: green; }")
                self.ui.txtConnect.setText("Conexión establecida.")

                # Encendemos los botonoes 
               
                self.manejoButton(True)

                # Procesamiento de Camara
                
                self.ui.procesador_camara.iniciar_camara()
                self.ui.procesador_camara.senal_actualizacion.connect(self.actualizar_interfaz)
                
                self.visCamera = True

                self.ui.RB_manual.setEnabled(True)
                self.ui.RB_auto.setEnabled(True)
                self.ui.RB_white.setEnabled(True)
                
                # Realiza la conexion 
                self.send_data.connect()
            else:
                self.ui.txtConnect.setText("No se pudo establecer la conexión.")
                

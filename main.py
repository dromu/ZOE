import sys
from PyQt5 import uic, QtWidgets
from wificonnector import WifiConnector
from MyApp import MyApp

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())

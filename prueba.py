import unittest
from unittest.mock import MagicMock
from main import run_zoe
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSlider, QLabel
from utils.MyApp import MyApp

class TestRunZoe(unittest.TestCase):

    def setUp(self):
        self.app = MagicMock()
        QtWidgets.QApplication = MagicMock(return_value=self.app)
        self.window = MagicMock()
        MyApp = MagicMock(return_value=self.window)

    def test_run_zoe(self):
        run_zoe()
        self.assertTrue(QtWidgets.QApplication.called)
        self.assertTrue(MyApp.called)
        self.assertTrue(self.window.showMaximized.called)
        self.assertTrue(self.app.exec_.called)
        self.assertTrue(sys.exit.called)

if __name__ == "__main__":
    unittest.main()

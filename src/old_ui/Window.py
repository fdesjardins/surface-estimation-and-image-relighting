import sys

from PySide import QtGui
from PySide import QtCore
from PySide.QtGui import QApplication
from PySide.QtGui import QMainWindow
from PySide.QtGui import QMessageBox

from ConsoleDialog import ConsoleDialog
from Display import Display
from MenuBar import MenuBar
from StatusBar import StatusBar
from UserInterfaces import DefaultUI

_size = _width,_height = 1024,768
        

class Application(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self)
        self.parent = parent
        self.setWindowTitle('imrenderin')
        
        ## Widgets
        self.menu_bar = MenuBar(self)
        self.menu_bar.setFixedHeight(25)
        self.status_bar = StatusBar(self)
        self.status_bar.setFixedHeight(35)
        
        ## Redirect stdout,stderr to dialog
        self.console = ConsoleDialog(sys.stdout)
        sys.stdout = self.console
        sys.stderr = self.console
        
        ## UI Elements
        self.display = Display(self)
        self.controls = DefaultUI(self, self.display)
        
        ## Layout
        vbox = QtGui.QVBoxLayout(self)
        vbox.addWidget(self.menu_bar)
        vbox.addWidget(self.controls)
        vbox.addWidget(self.status_bar)
        vbox.setSpacing(2)
        vbox.setContentsMargins(2,2,2,2)
        
        self.setLayout(vbox)
        self.setMinimumWidth(200)
        self.setMinimumHeight(150)
        self.resize(_width,_height)
        
    def about(self):
        msg = '''
About this thing
'''
        mb = QMessageBox(self)
        mb.setText(msg.strip())
        mb.setIcon(QtGui.QMessageBox.Information)
        mb.setWindowTitle('About')
        mb.show()
        
    def showConsole(self):
        self.console.show()
        
    def help(self):
        msg = '''
Don't Panic!
'''
        mb = QMessageBox(self)
        mb.setText(msg.strip())
        mb.setIcon(QtGui.QMessageBox.Information)
        mb.setWindowTitle('About')
        mb.show()
        
    def open(self):
        fd = QtGui.QFileDialog()
        path = fd.getOpenFileName(None, 'Open image file...', '')
        self.display.imshow(path)

    def toggleFullscreen(self):
        self.showNormal() if self.isFullScreen() else self.showFullScreen()
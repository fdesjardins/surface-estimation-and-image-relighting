from PySide import QtCore
from PySide import QtGui
from PySide.QtGui import QStatusBar
from PySide.QtGui import QLabel
from PySide.QtGui import QPalette

class StatusBar(QtGui.QStatusBar):
    def __init__(self, parent = None):
        QtGui.QStatusBar.__init__(self)
        self.parent = parent
        
        self.status_text = QLabel('')
        self.addWidget(self.status_text, 1)

        style = 'QStatusBar { font: 14px; left: 30px; \
                              background-color: rgb(245,245,245); \
                              border: 1px solid rgb(185,185,185); \
                              border-radius: 0px;}'
        self.setStyleSheet(style)
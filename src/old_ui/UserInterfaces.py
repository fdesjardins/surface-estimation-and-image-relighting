from PySide import QtCore
from PySide import QtGui

class DefaultUI(QtGui.QWidget):
    def __init__(self, parent=None, display=None):
        QtGui.QWidget.__init__(self)
        
        ## adjust layout
        grid = QtGui.QGridLayout()
        grid.addWidget(display)
        grid.setContentsMargins(0,0,0,0)
        self.setLayout(grid)
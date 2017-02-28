from PySide import QtGui
from PySide.QtGui import QDialog
from PySide.QtGui import QHBoxLayout
from PySide.QtGui import QTextEdit

class ConsoleDialog(QtGui.QDialog):
    def __init__(self, stream=None):
        QtGui.QDialog.__init__(self)
        
        self.stream = stream
        self.setWindowTitle('Console Messages')
        self.layout=QHBoxLayout(self)
        self.layout.setSpacing(6)
        self.layout.setContentsMargins(3,3,3,3)
        self.edit = QTextEdit(self)
        self.edit.setReadOnly(True)
        self.layout.addWidget(self.edit)
        self.resize(450,250)
        
    def write(self, msg):
        self.edit.moveCursor(QtGui.QTextCursor.End)
        self.edit.insertPlainText(msg)
        if self.stream:
            self.stream.write(msg)
        
from PySide import QtCore
from PySide import QtGui

from ImagePixmapItem import ImagePixmapItem

class Display(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, None)
        self.parent = parent
        
        ## Create graphicsview and scene
        self.gview = QtGui.QGraphicsView(self)
        self.scene = QtGui.QGraphicsScene(self)
        self.gview.setScene(self.scene)
        self.gview.setStyleSheet("QGraphicsView { border: 1px solid rgb(185,185,185); \
                                                  border-radius: 3px; }")
        
        ## Create background gradient
        rad = QtGui.QRadialGradient(450, 350, 2000)
        rad.setColorAt(0, QtGui.QColor(125,125,125))
        rad.setColorAt(1, QtGui.QColor(250,250,255))
        rad.setSpread(QtGui.QGradient.RepeatSpread)
        self.scene.setBackgroundBrush(rad)
        
        ## Create layout
        hbox = QtGui.QHBoxLayout(self)
        hbox.addWidget(self.gview)
        self.setLayout(hbox)
        hbox.setContentsMargins(0,0,0,0)
        hbox.setSpacing(0)
        
        self.gview.show()
        
    def imshow(self, image):
        
        if type(image) == str:
            image = QtGui.QPixmap(image)
        elif type(image) == tuple:
            image = QtGui.QPixmap(str(image[0]))

        self.scene.addItem(ImagePixmapItem(image))
        self.refresh()
        
    def refresh(self):
        self.gview.update()
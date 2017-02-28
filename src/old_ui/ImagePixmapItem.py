from PySide import QtCore
from PySide import QtGui

class ImagePixmapItem(QtGui.QGraphicsPixmapItem):
    def __init__(self, pmap):
        QtGui.QGraphicsPixmapItem.__init__(self, pmap)
        self.src_pmap = pmap
        self.old_pmap = pmap
        self.selected = False
        
    def mousePressEvent(self, event):
        try:
            if self.source != None:
                self.source.selectTile(self.uid)
        except Exception:
            pass
        
    def setSelected(self, bool):   
        if bool:
            if self.selected == False:
                ## Draw rectangle around edge of pixmap
                self.selected = True
                self.old_pmap = self.pixmap()
                self.new_pmap = drawBorder(self.old_pmap, 'yellow')
                self.setPixmap(self.new_pmap)
        else:
            self.setPixmap(self.old_pmap)
            self.selected = False
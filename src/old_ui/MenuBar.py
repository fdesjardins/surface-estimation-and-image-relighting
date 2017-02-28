from PySide import QtCore
from PySide import QtGui
from PySide.QtGui import QMessageBox
from PySide.QtGui import QFileDialog

class MenuBar(QtGui.QMenuBar):
    def __init__(self, parent=None):
        QtGui.QMenuBar.__init__(self)
        self.parent = parent
        
        self.createFileMenu()
        self.createEditMenu()
        self.createViewMenu()
        self.createHelpMenu()
        
    def createAction(self, text, shortcut=None, tip=None, slot=None, 
                        checkable=False, duration=2500, icon=None):
    
        action = QtGui.QAction(text, self.parent)
        
        ## Set action attributes
        if icon is not None:
            _icon = QtGui.QIcon()
            _icon.addPixmap(QtGui.QPixmap("%s.png" % icon), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            action.setIcon(_icon)
            action.setIconVisibleInMenu(True)
        if shortcut is not None: 
            action.setShortcut(shortcut)
        if tip is not None: 
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if checkable:
            action.setCheckable(True)
        
        ## Set action signal/slot connections
        self.connect(action, QtCore.SIGNAL('triggered()'), slot)
        self.connect(action, QtCore.SIGNAL('hovered()'), 
                     (lambda x=duration: self.parent.status_bar.showMessage(action.statusTip(), x)))
        
        return action
        
    def createEditMenu(self):    
        edit_menu = self.addMenu('&Edit')
        settings_action = self.createAction("&Settings",
                                             tip = "Change the program's settings",
                                             slot = self.parent.toggleFullscreen,
                                             checkable = False,
                                             icon = 'data/icons/properties')
        edit_menu.addAction(settings_action)
        
    def createFileMenu(self):
        file_menu = self.addMenu('&File')
        open_action = self.createAction('&Open',
                                         'Ctrl+O',
                                         'Open an image to work with',
                                         slot = self.parent.open,
                                         icon = 'data/icons/open')
        quit_action = self.createAction('&Quit',
                                         'Ctrl+Q',
                                         'Close imrenderin',
                                         slot = self.parent.close,
                                         icon = 'data/icons/close')
        file_menu.addAction(open_action)
        file_menu.addAction(quit_action)
        
    def createHelpMenu(self):
        help_menu = self.addMenu('&Help')
        about_action = self.createAction('&About',
                                          None,
                                          'About imrenderin',
                                          slot = self.parent.about,
                                          icon = 'data/icons/help_about')
        help_action = self.createAction('&Help',
                                         'F1',
                                         'Help using imrenderin',
                                         slot = self.parent.help,
                                         icon = 'data/icons/help')
        help_menu.addAction(help_action)
        help_menu.addSeparator()
        help_menu.addAction(about_action)
        
    def createViewMenu(self):
        view_menu = self.addMenu('&View')
        console_action = self.createAction("&Console Window", tip = "View console messages and errors",
                                            slot = self.parent.showConsole, checkable = False,
                                            icon = 'data/icons/console')
        fullscreen_action = self.createAction("&Fullscreen", "Ctrl+F", "Show in full screen mode",
                                                    slot = self.parent.toggleFullscreen, checkable = True,
                                                    icon = 'data/icons/fullscreen')
        view_menu.addAction(console_action)
        view_menu.addAction(fullscreen_action)
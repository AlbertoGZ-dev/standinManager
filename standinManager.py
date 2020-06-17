'''
-----------------------------------------
standinManager is a tool to change 
massively properties in standin nodes.

Autor: AlbertoGZ
Email: albertogzonline@gmail.com
-----------------------------------------
'''

from PySide2 import QtCore, QtWidgets, QtGui
from shiboken2 import wrapInstance
from collections import OrderedDict

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui
import maya.api.OpenMaya as om



# GENERAL VARS
version = '0.1.0'
winWidth = 505
winHeight = 305
red = '#872323'
green = '#207527'


def getMainWindow():
    main_window_ptr = omui.MQtUtil.mainWindow()
    mainWindow = wrapInstance(long(main_window_ptr), QtWidgets.QWidget)
    return mainWindow


class standinManager(QtWidgets.QMainWindow):

    def __init__(self, parent=getMainWindow()):
        super(standinManager, self).__init__(parent, QtCore.Qt.WindowStaysOnTopHint)

        # Creates object, Title Name and Adds a QtWidget as our central widget/Main Layout
        self.setObjectName('standinManagerUI')
        self.setWindowTitle('Standin Manager' + ' ' + 'v' + version)
        mainLayout = QtWidgets.QWidget(self)
        self.setCentralWidget(mainLayout)
        
        # Adding a Horizontal layout to divide the UI in columns
        columns = QtWidgets.QHBoxLayout(mainLayout)

        # Creating N vertical layout
        self.col1 = QtWidgets.QVBoxLayout()
        self.col2 = QtWidgets.QVBoxLayout()

        # Set columns for each layout using stretch policy
        columns.addLayout(self.col1, 1)
        columns.addLayout(self.col2, 3)
        
        # Adding UI elements
        layout1 = QtWidgets.QVBoxLayout()
        layout2 = QtWidgets.QVBoxLayout()
        layout2A = QtWidgets.QHBoxLayout()
        layout2B = QtWidgets.QHBoxLayout()

        self.col1.addLayout(layout1)
        self.col2.addLayout(layout2)
        layout2.addLayout(layout2A)
        layout2.addLayout(layout2B)



        ### UI ELEMENTS
        #     
        # SearchBox input for filter list
        self.assSearchBox = QtWidgets.QLineEdit('', self)
        self.assRegex = QtCore.QRegExp('[0-9A-Za-z_]+')
        self.assValidator = QtGui.QRegExpValidator(self.assRegex)
        self.assSearchBox.setValidator(self.assValidator)
        self.assSearchBox.textChanged.connect(self.assFilter)

        # List of standins
        self.assQList = QtWidgets.QListWidget(self)
        self.assQList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.assQList.setMinimumWidth(150)
        self.assQList.itemClicked.connect(self.assSel)

        # select All button
        self.selAllBtn = QtWidgets.QPushButton('Select All')
        self.selAllBtn.clicked.connect(self.selectAll)

        # select None button
        self.selNoneBtn = QtWidgets.QPushButton('Select None')
        self.selNoneBtn.clicked.connect(self.selectNone)

        # Reload button
        self.reloadBtn = QtWidgets.QPushButton('Reload')
        self.reloadBtn.clicked.connect(self.reload)

        # View Mode label
        self.viewModeLabel = QtWidgets.QLabel('View Mode')
        self.viewModeLabel.setFixedWidth(60)
        self.viewModeLabel.setAlignment(QtCore.Qt.AlignRight)

        # Combobox selector for View Mode
        self.viewModeComboBox = QtWidgets.QComboBox(self)
        self.viewModeComboBox.setMaximumWidth(170)
        self.viewModeComboBox.addItem('Bounding Box', '0')
        self.viewModeComboBox.addItem('Per Object Bounding Box', '1')
        self.viewModeComboBox.addItem('Polywire', '2')
        self.viewModeComboBox.addItem('Wireframe', '3')
        self.viewModeComboBox.addItem('Point Cloud', '4')
        self.viewModeComboBox.addItem('Shaded polywire', '5')
        self.viewModeComboBox.addItem('Shaded', '6')
        self.viewModeComboBox.activated[str].connect(self.selViewMode)

        # File path
        self.fileLabel = QtWidgets.QLabel('File')
        self.fileLabel.setFixedWidth(60)
        self.fileLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.filePath = QtWidgets.QLineEdit(self)

        self.getBtn = QtWidgets.QPushButton('Open')
        self.getBtn.setFixedWidth(35)
        self.getBtn.setFixedHeight(18)
        self.getBtn.clicked.connect(self.getPath)

        self.setBtn = QtWidgets.QPushButton('Set')
        self.setBtn.setFixedWidth(35)
        self.setBtn.setFixedHeight(18)
        self.setBtn.clicked.connect(self.setPath)

        # Add status bar widget
        self.statusBar = QtWidgets.QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.messageChanged.connect(self.statusChanged)

        # Add elements to layout
        layout1.addWidget(self.assSearchBox)
        layout1.addWidget(self.assQList)
        #layout1.addWidget(self.selAllBtn)
        #layout1.addWidget(self.selNoneBtn)
        layout1.addWidget(self.reloadBtn)
        
        layout2B.addWidget(self.viewModeLabel)
        layout2B.addWidget(self.viewModeComboBox, alignment=QtCore.Qt.AlignLeft)
        layout2A.addWidget(self.fileLabel)
        layout2A.addWidget(self.filePath)
        layout2A.addWidget(self.getBtn)
        layout2A.addWidget(self.setBtn)
                
        self.resize(winWidth, winHeight)


        ### Load all standins from scene    
        self.assLoad()


    
    ### Filter ass name in assList
    def assFilter(self):
        textFilter = str(self.assSearchBox.text()).lower()
        if not textFilter:
            for row in range(self.assQList.count()):
                self.assQList.setRowHidden(row, False)
        else:
            for row in range(self.assQList.count()):
                if textFilter in str(self.assQList.item(row).text()).lower():
                    self.assQList.setRowHidden(row, False)
                else:
                    self.assQList.setRowHidden(row, True)
    

    def reload(self):
        self.assQList.clear()
        del assSelected[:]
        self.assLoad()


    def assLoad(self):
        global assList
        assList = []
        assList.append(cmds.ls(type='aiStandIn'))
        
        for ass in assList:
            ass.sort()
            self.assQList.addItems(ass)


    ### Get selected standins in assQList
    def assSel(self, item):
        global assSelected

        if self.assQList.currentItem():
            items = self.assQList.selectedItems()
            assSelected = []
            for i in items:
                assSelected.append(i.text())
        
                                 
    ### Set View Mode
    def selViewMode(self):
        viewMode = self.viewModeComboBox.itemData(self.viewModeComboBox.currentIndex())
       
        if assSelected != []:
            for ass in assSelected:
                cmds.setAttr(ass + '.mode', int(viewMode))
            #del assSelected[:]

            self.statusBar.showMessage('Changed view mode successfully!', 4000)
            self.statusBar.setStyleSheet('background-color:' + green)

        else:
            self.statusBar.showMessage('Nothing selected', 4000)
            self.statusBar.setStyleSheet('background-color:' + red)


    ### Set ass file path 
    def setPath(self):
        filePath = self.filePath.text()
       
        if assSelected != []:
            for ass in assSelected:
                cmds.setAttr(ass + '.dso', str(filePath), type='string')

            self.statusBar.showMessage('Changed ass file successfully!', 4000)
            self.statusBar.setStyleSheet('background-color:' + green)

        else:
            self.statusBar.showMessage('Nothing selected', 4000)
            self.statusBar.setStyleSheet('background-color:' + red)


    def getPath(self, name='Open'):
        dialog = QtWidgets.QFileDialog()
        filename = dialog.getOpenFileName(self, name)
        if len(filename[0]) > 0:
            self.filePath.setText(filename[0])
            return filename[0] 
    
   
    def statusChanged(self, args):
        if not args:
            self.statusBar.setStyleSheet('background-color:none')
      

    def selectAll(self):
        ''' wip '''
        global assSelected
        items = self.assQList.findItems('*', QtCore.Qt.MatchWildcard)
        
        assSelected = []
        for ass in items:
            assSelected.append(ass)
        self.statusBar.showMessage(str(assSelected), 2000)

        
    def selectNone(self):
        self.assQList.clearSelection()
        del assSelected[:]
        allSelected = 0
        self.statusBar.showMessage(str(allSelected), 2000)
        return allSelected

     
    def closeEvent(self, event):
        del assSelected[:]
        pass


if __name__ == '__main__':
  try:
      win.close()
  except:
      pass
  win = standinManager(parent=getMainWindow())
  win.show()
  win.raise_()

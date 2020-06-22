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
from PIL import ImageColor




import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui
import maya.api.OpenMaya as om
import re



# GENERAL VARS
version = '0.1.2'
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
        self.setWindowTitle('StandIn Manager' + ' ' + 'v' + version)
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
        
        # Adding layouts
        layout1 = QtWidgets.QVBoxLayout()
        layout1A = QtWidgets.QVBoxLayout()
        layout1B = QtWidgets.QHBoxLayout()
        layout2 = QtWidgets.QVBoxLayout()
        layout2A = QtWidgets.QGridLayout()
        layout2A.setHorizontalSpacing(5)
        layout2A.setVerticalSpacing(10)
        
        self.col1.addLayout(layout1)
        self.col2.addLayout(layout2)        
        layout1.addLayout(layout1A)
        layout1.addLayout(layout1B)
        layout2.addLayout(layout2A)


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
        self.assQList.itemSelectionChanged.connect(self.assSel)

        self.selectLabel = QtWidgets.QLabel('Select')
        # select All button
        self.selAllBtn = QtWidgets.QPushButton('All')
        self.selAllBtn.setFixedWidth(50)
        self.selAllBtn.clicked.connect(self.selectAll)

        # select None button
        self.selNoneBtn = QtWidgets.QPushButton('None')
        self.selNoneBtn.setFixedWidth(50)
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

        # Color selector
        self.colorPicker = QtWidgets.QColorDialog('Color')
        self.colorLabel = QtWidgets.QLabel('Wire color')
        self.colorLabel.setFixedWidth(60)
        self.colorLabel.setAlignment(QtCore.Qt.AlignRight)
        self.colorBtn = QtWidgets.QPushButton('')
        self.colorBtn.setFixedWidth(170)
        self.colorBtn.setFixedHeight(18)
        self.colorBtn.setStyleSheet('background-color:rgb(0,0,0); color:black')
        self.colorBtn.clicked.connect(self.wireColor)

        # Status bar
        self.statusBar = QtWidgets.QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.messageChanged.connect(self.statusChanged)

        # Adding all elements to layouts
        layout1A.addWidget(self.assSearchBox)
        layout1A.addWidget(self.assQList)
        layout1B.addWidget(self.selectLabel)
        layout1B.addWidget(self.selAllBtn)
        layout1B.addWidget(self.selNoneBtn)
        layout1.addWidget(self.reloadBtn)
        
        layout2A.addWidget(self.fileLabel, 1, 0)
        layout2A.addWidget(self.filePath, 1, 1)
        layout2A.addWidget(self.getBtn, 1, 2)
        layout2A.addWidget(self.setBtn, 1, 3)
        layout2A.addWidget(self.viewModeLabel, 2, 0)
        layout2A.addWidget(self.viewModeComboBox, 2, 1)
        layout2A.addWidget(self.colorLabel, 3, 0)
        layout2A.addWidget(self.colorBtn, 3, 1)

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
            ass = [w.replace('Shape', '') for w in ass]
            ass.sort()
            self.assQList.addItems(ass)


    ### Get selected standins in assQList
    def assSel(self):
        global assSelected

        items = self.assQList.selectedItems()
        assSelected = []
        for i in items:
            assSelected.append(i.text())
        #self.statusBar.showMessage(str(assSelected), 4000) #for testing
    
                                 
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
    


    def wireColor(self):
        
        if assSelected != []:
            color = QtWidgets.QColorDialog.getColor()
            rgbInt = ImageColor.getcolor(str(color.name()), "RGB")  
            rgbFloat = tuple(int(color.name()[i:i + 2], 16) / 255. for i in (1, 3, 5))
            r = round(rgbFloat[0], 3)
            g = round(rgbFloat[1], 3)
            b = round(rgbFloat[2], 3)
            colorFloat = 'r:'+str(r) +' g:'+ str(g) +' b:'+ str(b) 

                
            if color.isValid():
                #self.colorBtn.setText(colorFloat)
                self.colorBtn.setStyleSheet('background-color: rgba'+str(rgbInt)+'; color:black')

                for ass in assSelected:
                    cmds.setAttr(ass + '.overrideEnabled', 1)
                    cmds.setAttr(ass + '.overrideRGBColors', 1)
                    cmds.setAttr(ass + '.overrideColorRGB', rgbFloat[0],rgbFloat[1],rgbFloat[2])
                
                    self.statusBar.showMessage('Changed color to ' + colorFloat + ' successfully!', 4000)
                    self.statusBar.setStyleSheet('background-color:' + green)
        else:
            self.statusBar.showMessage('Nothing selected', 4000)
            self.statusBar.setStyleSheet('background-color:' + red)
        


    def statusChanged(self, args):
        if not args:
            self.statusBar.setStyleSheet('background-color:none')
      

    def selectAll(self):
        self.assQList.selectAll()
        #self.statusBar.showMessage(str(assSelected), 2000) # for testing

        
    def selectNone(self):
        self.assQList.clearSelection()
        del assSelected[:]
        #self.statusBar.showMessage(str(assSelected), 2000) #for testing

     
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

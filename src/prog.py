#!/usr/bin/env python

##############
# Cose da fare:
# 2) esportare
# 3) raggio di azione
##############


import sys
#PyQt4 or PySide
#import PyQt4.QtCore as QC
#import PyQt4.QtGui as QG
#import PyQt4.QtWebKit as QWK
import PySide.QtCore as QC
import PySide.QtGui as QG
import PySide.QtWebKit as QWK


class ChromePage(QWK.QWebPage):
    "QWebPage modified in order to use normal template for map, click events, etc."
    def userAgentForUrl(self, url):
        return 'Chrome/1.0'

class browser(QWK.QWebView):
    def __init__(self):
        super(browser,self).__init__()
        self.dataFromJava = None
        self.setPage(ChromePage())
        self.load(QC.QUrl("page.html"))
        self.frame = self.page().mainFrame()
        
    def mouseReleaseEvent(self, event):
        QWK.QWebView.mouseReleaseEvent(self,event)
        self.dataFromJava = self.frame.evaluateJavaScript("getPoly()")
        selectedItem = self.frame.evaluateJavaScript("getSelectedItem()")
        self.emit(QC.SIGNAL("newDataFromJava(int)"),selectedItem)
        
    def keyReleaseEvent(self, event):
        QWK.QWebView.keyReleaseEvent(self,event)
        self.dataFromJava = self.frame.evaluateJavaScript("getPoly()")
        selectedItem = self.frame.evaluateJavaScript("getSelectedItem()")
        self.emit(QC.SIGNAL("newDataFromJava(int)"),selectedItem)
        
    def selectItem(self,item):
        itemWeb = self.frame.evaluateJavaScript("getSelectedItem()")
        if (itemWeb != item):
            self.frame.evaluateJavaScript("selectItemFromInt(%i)" %item)
            
    def removeItem(self,index):
        self.frame.evaluateJavaScript("removeItemFromInt(%i)" %index)
    
    def clearAll(self):
        self.frame.evaluateJavaScript("clearAll()")

class pathTable(QG.QTableWidget):
    def __init__(self):
        super(pathTable,self).__init__()
        self.setColumnCount(4)
        #self.setTextAlignment(QC.Qt.AlignVCenter);
        widthFirst = 20
        widthCol   = 80
        self.setColumnWidth(0,widthFirst)
        self.setColumnWidth(1,widthCol)
        self.setColumnWidth(2,widthCol)
        self.setColumnWidth(3,widthCol)
        self.setHorizontalHeaderLabels( ["#","X","Y","Z"] )
        self.setMinimumWidth(3*widthCol+widthFirst+3)
        self.verticalHeader().hide()
        self.setSelectionBehavior(QG.QAbstractItemView.SelectRows)
        self.connect(self, QC.SIGNAL('itemSelectionChanged()'), self.itemSelChanged)
    
    
    def keyReleaseEvent(self, event):
        QG.QTableWidget.keyReleaseEvent(self,event)
        if (event.key() == QC.Qt.Key_Backspace):
            if (len(self.selectedIndexes()) != 0):
                i = self.currentRow()
                self.removeRow(i)
                for irow in range(self.rowCount()):
                    item = self.item(irow,0)
                    item.setData(QC.Qt.DisplayRole,"%i" %irow)
                #!!!!!!!!!!!!!!!!rifai la numerazione della prima colonna
                self.emit(QC.SIGNAL("removedRow(int)"), i)
            

#non devo generare segnale itemSelectionChanged quando lo cambio a mano
    def itemSelChanged(self):
        if self.hasFocus():
            if (len(self.selectedIndexes()) != 0):
                self.emit(QC.SIGNAL("newSelection(int)"), self.currentRow())
            else:
                print "No item selected"

        
    def update(self,data,selectedItem):
        self.clearContents()
        nrow = len(data)
        self.setRowCount(len(data))
        for i in range(nrow):
            self.mySetItem(i,0,i)
            self.mySetItem(i,1,data[i]['Ia'])
            self.mySetItem(i,2,data[i]['Ha'])
        if (selectedItem>=0):
            self.selectRow(selectedItem)
            
    def mySetItem(self,row,col,data):
        item = QG.QTableWidgetItem()
        font = QG.QFont()
        font.setPointSize(10)
        item.setFont(font)
        item.setTextAlignment(QC.Qt.AlignCenter)
        flags = QC.Qt.NoItemFlags | QC.Qt.ItemIsEnabled | QC.Qt.ItemIsSelectable
        if (col==0):
            fmt = "%i"
        else:
            flags = flags | QC.Qt.ItemIsEditable
            fmt = "%.7f"
        item.setFlags(flags)
        item.setData(QC.Qt.DisplayRole,fmt %data)
        self.setItem(row,col,item)
        
    def clearAll(self):
        self.clearContents()
        self.setRowCount(0)

class pathCreator(QG.QMainWindow):
#Widget):
    def __init__(self):
        super(pathCreator,self).__init__()
        self.initUI()
        
        #QWK.QWebSettings.globalSettings().setAttribute(QWK.QWebSettings.PluginsEnabled, True);
        
        self.statusBar().showMessage('Ready')
        
        self.connect(self.web,   QC.SIGNAL("newDataFromJava(int)"), lambda x: self.table.update(self.web.dataFromJava,x) )
        self.connect(self.table, QC.SIGNAL("newSelection(int)"), self.web.selectItem )
        self.connect(self.table, QC.SIGNAL('removedRow(int)'), self.web.removeItem )
        self.connect(self.clearButton, QC.SIGNAL("clicked()"), self.clearAll)
        self.connect(self.traslateButton, QC.SIGNAL("clicked()"), self.traslate)

    def initUI(self):
        self.main = QG.QWidget(self)
        self.setCentralWidget(self.main)
        
        self.table = pathTable()
        self.web = browser()
        self.clearButton = QG.QPushButton('Clear all', self)
        self.traslateButton = QG.QPushButton('Traslate', self)
        
        hbox0 = QG.QHBoxLayout()
        hbox0.addWidget(self.traslateButton)
        hbox0.addWidget(self.clearButton)
        
        vbox = QG.QVBoxLayout()
        vbox.addWidget(self.table)
        vbox.addLayout(hbox0)

        hbox = QG.QHBoxLayout()
        hbox.addLayout(vbox)
        hbox.addWidget(self.web)
        self.main.setLayout(hbox)
        #splitter = QG.QSplitter(self)

        exit = QG.QAction( 'Exit', self )
        self.connect(exit, QC.SIGNAL('triggered()'), QC.SLOT('close()'))
        menubar = self.menuBar()
        file = menubar.addMenu('&File')
        file.addAction(exit)
        
    def clearAll(self):
        self.web.clearAll()
        self.table.clearAll()
    
    def traslate(self):
        dw = QG.QDialog()
        #vector = QG.QTableWidget(dw)
        #vector.setColumnCount(3)
        #vector.setRowCount(1)
        #vector.verticalHeader().hide()
        #vector.setHorizontalHeaderLabels( ["X","Y","Z"] )

        grid = QG.QGridLayout()

        xlabel = QG.QLabel("X: ")
        xval = QG.QDoubleSpinBox()
        xval.setMinimum(-100)
        xval.setMaximum(100)
        xval.setSingleStep(1.0)
        xval.setValue(0.0)
        
        ylabel = QG.QLabel("Y: ")
        yval = QG.QDoubleSpinBox()
        yval.setMinimum(-100)
        yval.setMaximum(100)
        yval.setSingleStep(1.0)
        yval.setValue(0.0)
        
        zlabel = QG.QLabel("Z: ")
        zval = QG.QDoubleSpinBox()
        zval.setMinimum(-100)
        zval.setMaximum(100)
        zval.setSingleStep(1.0)
        zval.setValue(0.0)
        
        grid.addWidget(xlabel,0,0)
        grid.addWidget(ylabel,1,0)
        grid.addWidget(zlabel,2,0)
        grid.addWidget(xval,0,1)
        grid.addWidget(yval,1,1)
        grid.addWidget(zval,2,1)

        ok = QG.QPushButton('Ok', dw)
        cancel = QG.QPushButton('Cancel', dw)
        
        hbox = QG.QHBoxLayout()
        hbox.addWidget(cancel)
        hbox.addWidget(ok)
        
        vbox = QG.QVBoxLayout()
        vbox.addLayout(grid)
        vbox.addLayout(hbox)
        
        dw.connect(ok, QC.SIGNAL('clicked()'), QC.SLOT('accept()'))
        dw.connect( cancel, QC.SIGNAL('clicked()'), QC.SLOT('reject()') )
        dw.setWindowTitle("Traslate")
        dw.setLayout(vbox)
        if dw.exec_():
            print "HELLO"
        
        
if __name__=='__main__':
    app = QG.QApplication(sys.argv)
    window = pathCreator()
    window.show()
    sys.exit(app.exec_())
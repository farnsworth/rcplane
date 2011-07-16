import pygame
import socket
import sys # controllare se e' necessario
from PySide import QtCore,QtGui

ENDCHAR = chr(64) # @ = 64, \xxf = 255
PORT = 50007

def getNewAddr():
    
    remote_host,val = QtGui.QInputDialog.getText(None,"Connect to ...","IP address:",text="0.rcplane")
    if (val):
        return (remote_host,PORT)

    return None
    
        
class joystickSelector(QtGui.QDialog):
    def __init__(self):
        super(joystickSelector, self).__init__()
        
        self.initUI()
        self.connect(self.ok, QtCore.SIGNAL('clicked()'), QtCore.SLOT('accept()'))
        self.connect(self.cancel, QtCore.SIGNAL('clicked()'), QtCore.SLOT('reject()') )
        self.connect(self.update, QtCore.SIGNAL('clicked()'), self.updateJoystickList)
        
        self.updateJoystickList()
        self.show()
    
    def initUI(self):
        self.setWindowTitle("Joystick choice")
        self.ok = QtGui.QPushButton('Ok', self)
        self.update = QtGui.QPushButton('Update', self)
        self.cancel = QtGui.QPushButton('Cancel', self)
        
        self.listWidget = QtGui.QListWidget()
        self.listWidget.setSelectionMode( QtGui.QAbstractItemView.SingleSelection )
        vbox = QtGui.QVBoxLayout()        
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.cancel)
        hbox.addWidget(self.update)
        hbox.addWidget(self.ok)
        vbox.addWidget(self.listWidget)            
        vbox.addLayout(hbox)
            
        self.setLayout(vbox)
        
    def updateJoystickList(self):
        if (pygame.joystick.get_init()):
            pygame.joystick.quit()
            
        pygame.joystick.init()
        
        self.list = []
        self.listWidget.clear()
        
        njoystick = pygame.joystick.get_count()
        for i in range(njoystick):
            self.list.append( pygame.joystick.Joystick(i).get_name() )
        
        self.listWidget.addItems(self.list)

        if (len(self.list)==0):
            self.ok.setDisabled(True)
        else:
            self.ok.setDisabled(False)
            self.listWidget.item(0).setSelected(True)


class joystickVisualizer(QtGui.QDialog):
    
    rectSide = 120
    dist = 10
    psize = 10
    bsize = 40
    connButSize = 15
    frameSize = 5
    
    def __init__(self,id,addr = None):
        super(joystickVisualizer, self).__init__()
        self.addr = addr
        self.socket = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        self.socket.settimeout(1.0)
        self.id = id
        self.initUI()
        self.initJoystick()
        
        #self.connect(self.openCloseButton, QtCore.SIGNAL('clicked()'), self.openClose)
        if (self.addr == None):
            self.connect(self.connectToButton, QtCore.SIGNAL('clicked()'), self.connectTo)

        self.timerCheckConnection = QtCore.QTimer()
        self.connect(self.timerCheckConnection, QtCore.SIGNAL("timeout()"), self.checkConnection )
        #self.timerCheckConnection.timeout.connect(self.checkConnection())
        #self.timerCheckConnection.setInterval(1000)
        self.timerCheckConnection.start(5000)

        self.show()

    def initUI(self):
        vbox = QtGui.QVBoxLayout()
        self.graphicsView = QtGui.QGraphicsView()
        self.graphicsView.setStyleSheet("background: transparent; border: none")
        vbox.addWidget(self.graphicsView)
        self.scene = QtGui.QGraphicsScene()
        self.graphicsView.setScene(self.scene)
        
        self.rBrush = QtGui.QBrush()
        self.rBrush.setStyle(QtCore.Qt.SolidPattern)
        self.rBrush.setColor( QtGui.QColor("red") )
        
        self.gBrush = QtGui.QBrush()
        self.gBrush.setStyle(QtCore.Qt.SolidPattern)
        self.gBrush.setColor( QtGui.QColor("green") )
        
        self.wBrush = QtGui.QBrush()
        self.wBrush.setStyle(QtCore.Qt.SolidPattern)
        self.wBrush.setColor( QtGui.QColor("white") )
        
        self.scene.setSceneRect(0,0,2*self.frameSize+self.dist+2*self.rectSide,2*self.frameSize+self.dist + self.rectSide + self.bsize)
        self.lr = QtGui.QGraphicsRectItem(self.frameSize,self.frameSize,self.rectSide,self.rectSide,None,self.scene)
        self.rr = QtGui.QGraphicsRectItem(+self.frameSize+self.dist+self.rectSide,self.frameSize,self.rectSide,self.rectSide,None,self.scene)
        self.lr.setBrush(self.wBrush)
        self.rr.setBrush(self.wBrush)
        
        self.lines = []
        self.lines.append( QtGui.QGraphicsLineItem(None,self.scene) )
        self.lines.append( QtGui.QGraphicsLineItem(None,self.scene) )
        self.lines.append( QtGui.QGraphicsLineItem(None,self.scene) )
        self.lines.append( QtGui.QGraphicsLineItem(None,self.scene) )
        
        self.circles = []
        self.circles.append( QtGui.QGraphicsEllipseItem(None,self.scene) ) 
        self.circles.append( QtGui.QGraphicsEllipseItem(None,self.scene) )
        self.circles[0].setBrush(self.rBrush)
        self.circles[1].setBrush(self.rBrush)
        self.circles[0].setPen( QtGui.QPen(QtCore.Qt.NoPen))
        self.circles[1].setPen( QtGui.QPen(QtCore.Qt.NoPen))
        
        self.buttons = []
        y = self.frameSize + self.dist+self.rectSide
        delta = (self.dist + 2*self.rectSide - self.bsize)/3
        self.buttons.append( QtGui.QGraphicsEllipseItem(self.frameSize,y,self.bsize,self.bsize,None,self.scene) )
        self.buttons.append( QtGui.QGraphicsEllipseItem(self.frameSize+delta  ,y,self.bsize,self.bsize,None,self.scene) )
        self.buttons.append( QtGui.QGraphicsEllipseItem(self.frameSize+2*delta,y,self.bsize,self.bsize,None,self.scene) )
        self.buttons.append( QtGui.QGraphicsEllipseItem(self.frameSize+3*delta,y,self.bsize,self.bsize,None,self.scene) )
        for b in self.buttons:
            b.setBrush(self.wBrush)
        x0 = 7
        y -= 2
        font = QtGui.QFont()
        font.setPointSize(30)
        temp = QtGui.QGraphicsTextItem("1",self.buttons[0])
        temp.setPos(x0 + self.frameSize,y)
        temp.setFont(font)
        temp = QtGui.QGraphicsTextItem("2",self.buttons[1])
        temp.setPos(x0 + self.frameSize+delta  ,y)
        temp.setFont(font)
        temp = QtGui.QGraphicsTextItem("3",self.buttons[2])
        temp.setPos(x0 + self.frameSize+2*delta,y)
        temp.setFont(font)
        temp = QtGui.QGraphicsTextItem("4",self.buttons[3])
        temp.setPos(x0 + self.frameSize+3*delta,y)
        temp.setFont(font)
        
        self.connCircle = QtGui.QGraphicsEllipseItem(self.frameSize+self.rectSide+self.dist/2-self.connButSize/2,
                                                     self.frameSize+self.dist+self.rectSide+self.bsize/2,
                                                     self.connButSize,
                                                     self.connButSize,None,self.scene)
        self.connCircle.setPen( QtGui.QPen(QtCore.Qt.NoPen))
        
        if (self.addr == None):
            self.connectToButton = QtGui.QPushButton('Connect to...', self)
            self.connectToButton.setFixedWidth(150)
            vbox.addWidget(self.connectToButton,0,QtCore.Qt.AlignCenter)
            self.connCircle.setBrush(self.rBrush)
        else:
            self.connCircle.setBrush(self.gBrush)
        
             
        self.setLayout(vbox)
        self.setWindowTitle(pygame.joystick.Joystick( self.id ).get_name())
        
        
    def checkConnection(self):
        if (self.addr != None):
            try:
                self.socket.sendto("c@",self.addr)
                self.socket.recvfrom(8)
                #self.connCircle.setBrush(self.gBrush)
            except Exception as e:
                self.resetConnection(e.__str__())
    
    def resetConnection(self,message=""):
        self.addr = None
        self.connCircle.setBrush(self.rBrush)
        self.connectToButton.setText("Connect to ...")
        if (message != ""):
            p = QtGui.QMessageBox()
            p.setText( "Error " + message)
            p.exec_()
            
    def connectTo(self):
        if (self.addr != None):
            self.resetConnection()
        else:
            self.addr = getNewAddr()
            if (self.addr != None):
                self.connectToButton.setText("Close connection")
                self.connCircle.setBrush(self.gBrush)
                self.checkConnection()
                


    def initJoystick(self):
        self.joystick = pygame.joystick.Joystick( self.id )
        self.joystick.init()
        pygame.display.init()
        pygame.event.set_allowed(None)
        pygame.event.set_allowed([pygame.JOYAXISMOTION,pygame.JOYBUTTONDOWN,pygame.JOYBUTTONUP])
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.joystickEvent)
        self.timer.start()
        self.lineaxes = [0,1,3,4]
        for axes in self.lineaxes:
            self.setAxes(axes,0.0)

        self.buttonibutton = [0,1,2,3]
                

    def closeEvent(self,e):
        QtGui.QGraphicsView.closeEvent(self,e)
        self.socket.close()
        if (self.joystick.get_init()):
            self.joystick.quit()
        if (pygame.joystick.get_init()):
            pygame.joystick.quit()
        if (pygame.display.get_init()):
            pygame.display.quit()
        self.timer.stop()
        self.timerCheckConnection.stop()
        
    def joystickEvent(self):
        le = pygame.event.get()
        for e in le:
            if (e.dict['joy']== self.id):
                string = None
                if ( e.type == pygame.JOYAXISMOTION ):
                    self.setAxes(e.dict['axis'],e.dict['value'])
                    if (self.addr != None) and (e.dict['axis'] != 2):
                        iaxis =e.dict['axis']
                        string = "A"+str(self.lineaxes.index(iaxis))+"%.2f" %e.dict['value']+ENDCHAR
                        print string
                elif ( e.type == pygame.JOYBUTTONDOWN ):
                    self.setButtonDown( e.dict['button'] )
                    if (self.addr != None):
                        string = "B"+str(e.dict['button'])+"D"+ENDCHAR
                elif ( e.type == pygame.JOYBUTTONUP ):
                    self.setButtonUp( e.dict['button'] )
                    if (self.addr != None):
                        string = "B"+str(e.dict['button'])+"U"+ENDCHAR
                        
                if (string != None) and (self.addr != None):
                    try:
                        self.socket.sendto(string,self.addr)
                    except Exception as inst:
                        self.resetConnection(inst.__str__())
                    
    def setButtonDown(self,ibutton):
        if (self.buttonibutton.count(ibutton) > 0):        
            b = self.buttonibutton.index(ibutton)
            self.buttons[b].setBrush(self.rBrush)
            
        
    
    def setButtonUp(self,ibutton):
        if (self.buttonibutton.count(ibutton) > 0):        
            b = self.buttonibutton.index(ibutton)
            self.buttons[b].setBrush(self.wBrush)
            
    def setAxes(self,iaxes,val):
        newVal = val*(self.rectSide/2)
        
        if (self.lineaxes.count(iaxes) > 0):        
            line = self.lineaxes.index(iaxes)
            
            if (line==0):
                x = self.frameSize+self.rectSide/2 + newVal
                f = (x, self.frameSize)
                t = (x, self.frameSize+self.rectSide)
                y = self.frameSize+self.rectSide/2 + self.joystick.get_axis( self.lineaxes[1] ) *(self.rectSide/2)
            elif (line==1):
                y = self.frameSize+self.rectSide/2 + newVal
                f = (self.frameSize,y)
                t = (self.frameSize+self.rectSide,y)
                x = self.frameSize+self.rectSide/2 + self.joystick.get_axis( self.lineaxes[0] ) *(self.rectSide/2)
            elif (line==2):
                x = self.frameSize + self.dist+3*self.rectSide/2 + newVal
                f = (x, self.frameSize )
                t = (x, self.frameSize+self.rectSide)
                y = self.frameSize+self.rectSide/2 + self.joystick.get_axis( self.lineaxes[3] ) *(self.rectSide/2)
            elif (line==3):
                y = self.frameSize+self.rectSide/2 + newVal
                f = (self.frameSize + self.dist+self.rectSide,y)
                t = (self.frameSize + self.dist+2*self.rectSide,y)
                x = self.frameSize + self.dist+3*self.rectSide/2 + self.joystick.get_axis( self.lineaxes[2] ) *(self.rectSide/2)
                
            x -= self.psize/2
            y -= self.psize/2
            
            if (line==0 or line==1):
                self.circles[0].setRect(x,y,self.psize,self.psize)
            if (line==2 or line==3):
                self.circles[1].setRect(x,y,self.psize,self.psize)
                
            self.lines[line].setLine(f[0],f[1],t[0],t[1])


def main():
    app = QtGui.QApplication(sys.argv)
    jS = joystickSelector()
    if jS.exec_():
        if (len(jS.listWidget.selectedItems()) == 1):
            id = jS.listWidget.selectedIndexes()[0].row()
            
            jV = joystickVisualizer( id )           
            jV.exec_()



if (__name__=='__main__'):
    main()
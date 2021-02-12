
import sys
import time

from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow,QPushButton, QLineEdit,QGridLayout,QMessageBox,QWidget,QPlainTextEdit,QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QProcess

temp=0
hh=None
nn=None
username=None
password=None
ser_address=None
ser_port = None
loc_port = None
import asyncio
import websockets

async def messag(us,pas):
    async with websockets.connect("ws://localhost:1239") as socket:
        print ("your message")
        await socket.send(us)
        await socket.send(pas)


class UIWindow(QWidget):
    def __init__(self, parent=None):
        super(UIWindow, self).__init__(parent)

        self.p = None

        self.btn = QPushButton("start process")
        self.btn.pressed.connect(self.start_process)
        self.btn2 = QPushButton("show bandwidth")
        self.btn2.pressed.connect(self.funct)
        self.btn3 = QPushButton("stop and quit")
        self.btn3.pressed.connect(self.killl)
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)

        self.l = QVBoxLayout()
        self.l.addWidget(self.btn)
        self.l.addWidget(self.text)
        self.l.addWidget(self.btn2)
        self.l.addWidget(self.btn3)
        self.setLayout(self.l)

    def killl(self):
        if self.p:
            self.p.kill()
            exit(1)
            sys.exit()

    def funct(self):
        global nn
        if hh and nn!=9999:
            asyncio.get_event_loop().run_until_complete(messag(username,password))
            nn = 9999

    def message(self,s):
        self.text.appendPlainText(s)

    def start_process(self):
         global hh
         if self.p is None:
            self.message("Executing process.")
            self.p = QProcess()
            self.p.readyReadStandardOutput.connect(self.handle_stdout)

            #为了看 错误

            #self.p.readyReadStandardError.connect(self.handle_stderr)

            self.p.stateChanged.connect(self.handle_state)
            self.p.finished.connect(self.process_finished) # Keep a reference to the QProcess (e.g. on self) while it's running.

            self.p.start("python3", ['ar.py','--port',str(loc_port),str(ser_address),str(ser_port)])
            hh="test"

    def handle_stderr(self):
        data = self.p.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        self.message(stderr)

    def handle_stdout(self):
        data = self.p.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.message(stdout)
        #print(stdout)
        #print(len(stdout))
        #print(type(stdout))
        length = len(stdout)
        #print(stdout[0])
        try:
            if stdout[length-1]=='h' and stdout[length-2]=='t' and stdout[length-5]=='_' and stdout[length-10]=='e':
                self.mess= QMessageBox()
                self.mess.setText("Server says wrong username or password,ByeBye!!")
                self.mess.exec_()
                if self.p:
                    self.p.kill()
                print("bye bye")
                exit(1)
                sys.exit()

        except Exception as err:
            print(err)
    def handle_state(self, state):
        states = {
            QProcess.NotRunning: 'Not running',
            QProcess.Starting: 'Starting',
            QProcess.Running: 'Running',
        }
        state_name = states[state]
        self.message(f"State changed: {state_name}")

    def process_finished(self):
        self.message("Process finished.")
        self.p = None



class UIToolTab(QWidget):
    def __init__(self, parent=None):
        super(UIToolTab, self).__init__(parent)

        self.layout = QGridLayout()

        self.label_name = QLabel('<font size = "4">Username </font>',self)

        self.lineEdit_username = QLineEdit()
        self.lineEdit_username.setPlaceholderText('enter your username')

        self.layout.addWidget(self.label_name,0,0)
        self.layout.addWidget(self.lineEdit_username,0,1)


        self.label_password = QLabel('<font size = "4"> Password </font>')

        self.lineEdit_password = QLineEdit()
        self.lineEdit_password.setPlaceholderText('enter your password')

        self.label_address = QLabel('<font size = "4">Server address </font>',self)
        self.lineEdit_address = QLineEdit()
        self.lineEdit_address.setPlaceholderText('enter the server address')

        self.label_port = QLabel('<font size = "4">Server port </font>',self)
        self.lineEdit_port = QLineEdit()
        self.lineEdit_port.setPlaceholderText('enter the server port')

        self.label_loc_port = QLabel('<font size = "4">local port </font>',self)
        self.lineEdit_loc_port= QLineEdit()
        self.lineEdit_loc_port.setPlaceholderText('enter your local port')


        self.layout.addWidget(self.label_password,1,0)
        self.layout.addWidget(self.lineEdit_password,1,1)



        self.layout.addWidget(self.label_address,2,0)
        self.layout.addWidget(self.lineEdit_address,2,1)

        self.layout.addWidget(self.label_port,3,0)
        self.layout.addWidget(self.lineEdit_port,3,1)

        self.layout.addWidget(self.label_loc_port,4,0)
        self.layout.addWidget(self.lineEdit_loc_port,4,1)



        self.button_login = QPushButton('确定')
        self.button_cancel = QPushButton('退出')

        self.layout.addWidget(self.button_login,5,0)
        self.layout.addWidget(self.button_cancel,5,2)

        self.layout.setRowMinimumHeight(5,75)

        self.button_Start = QPushButton('go to main window')


        self.button_login.clicked.connect(self.check_text)
        self.button_cancel.clicked.connect(self.exi)
        self.setLayout(self.layout)

    def exi(self):
        exit(1)
    def check_text(self):

        global username
        global password
        global ser_address
        global ser_port
        global loc_port
        self.message= QMessageBox()

        if not self.lineEdit_username.text() or not self.lineEdit_password.text():
                self.message.setText('empty username or password')
                self.message.exec_()

        else :
            ser_address = self.lineEdit_address.text()
            ser_port = self.lineEdit_port.text()
            self.layout.addWidget(self.button_Start,5,1)
            username = self.lineEdit_username.text()
            password = self.lineEdit_password.text()
            loc_port = self.lineEdit_loc_port.text()





class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setGeometry(50, 50, 400, 450)
        self.setFixedSize(400, 450)
        self.startUIToolTab()

    def startUIToolTab(self):
        self.ToolTab = UIToolTab(self)
        self.setWindowTitle("login_tab")
        self.setCentralWidget(self.ToolTab)

        self.ToolTab.button_Start.clicked.connect(self.startUIWindow)

        self.show()

    def startUIWindow(self):
        self.Window = UIWindow(self)
        self.setWindowTitle(str(ser_address)+'   '+str(ser_port))
        self.setCentralWidget(self.Window)

        self.show()




if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec_())




#v1.4.0
#v1.4.1

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
#from PyQt5.QtWebKitWidgets import *
from PyQt5.QtWebEngineWidgets import *

import sys
import os
import time



def rais(text):
    from subprocess import call
    call('start echo OMSSD Browser error: %s'%(text),shell=True)
    raise
def raisSetting(fname,text):
    rais('Error with file "settings/%s": %s'%(fname,text))

def getSettingRaw(setName):
    filedir = 'settings/%s.txt'%(setName)
    setName = filedir
    try:
        f = open(filedir,'r')
    except FileNotFoundError:
        rais('Missing file "%s"'%(filedir))
    else:
        toreturn = f.readline()
        if toreturn[-1] == '\n': toreturn = toreturn[:-1]
        f.close()
        return toreturn
def getSettingBool(setName):
    value = getSettingRaw(setName)
    if value == 'True': return True
    elif value == 'False': return False
    else:
        raisSetting(setName,'value should be "True" or "False", but is instead "%s"'%(value))
def getSettingStr(setName):
    return getSettingRaw(setName)
def getSettingSize(setName):
    data = getSettingRaw(setName)
    if data.count(',') != 1:
        raisSetting(setName,'there should be 1 "," not %s'%(data.count(',')))
    data = data.split(',')
    try:x = int(data[0])
    except ValueError: raisSetting(setName,'the first value should be an integer, not "%s"'%(data[0]))
    try:y = int(data[1])
    except ValueError: raisSetting(setName,'the second value should be an integer, not "%s"'%(data[1]))
    return x,y

class Browser(QWebEngineView):
    def createWindow(self,mode):
        window = create_new_tab()
        #if mode == QWebPage.WebModalDialog:
        #    print('c')
        #window.setWindowModality(Qt.ApplicationModal)
        return window.browser

class MainWindow(QMainWindow):
    def __init__(self,*args,**kwargs):
        super(MainWindow,self).__init__(*args,**kwargs)

        self.browser = Browser()

        self.setCentralWidget(self.browser)

        navtb = QToolBar('Ne natiskai')
        #navtb.setIconSize(QSize(30,30))
        navtb.setMovable(getSettingBool('navtbMovable'))
        navtb.removeAction(QAction('kur',navtb))
        self.addToolBar(navtb)

        if getSettingBool('enableBackBtn'):
            back_btn = QAction('Back',self)
            back_btn.setStatusTip('Back to the previous page')
            back_btn.triggered.connect(self.browser.back)
            navtb.addAction(back_btn)

        if getSettingBool('enableForwardBtn'):
            next_btn = QAction('Forward',self)
            next_btn.setStatusTip('Forward to next page')
            #next_btn.setShortcut('mouse4') ne raboti bash
            next_btn.triggered.connect(self.browser.forward)
            navtb.addAction(next_btn)

        if getSettingBool('enableReloadBtn'):
            reload_btn = QAction('Rload',self)
            reload_btn.setStatusTip('Reload')
            reload_btn.triggered.connect(self.browser.reload)
            navtb.addAction(reload_btn)

        if getSettingBool('enableHomeBtn'):
            home_btn = QAction('Home',self)
            home_btn.setStatusTip('Home')
            home_btn.triggered.connect(lambda:navigate_home(self))
            navtb.addAction(home_btn)

        if getSettingBool('enableStopBtn'): 
            stop_btn = QAction('Stop',self)
            stop_btn.setStatusTip('Stop loading current page')
            stop_btn.triggered.connect(self.browser.stop)
            navtb.addAction(stop_btn)

        #if getSettingBool('enableHttpsIcon'):
        #    self.httpsicon = QLabel()
        #    navtb.addWidget(self.httpsicon)
            
        if getSettingBool('enableUrlBar'):
            self.urlbar = QLineEdit()
            self.urlbar.returnPressed.connect(lambda:self.navigate_to_url(self))
            navtb.addWidget(self.urlbar)
            self.browser.urlChanged.connect(lambda q:update_urlbar(self,q))

        add_tab_btn = QAction('New tab',self)
        add_tab_btn.triggered.connect(create_new_tab)
        navtb.addAction(add_tab_btn)


        self.browser.loadFinished.connect(lambda:load_finished(self))
            

        if getSettingBool('enableDownloads'):
            self.browser.page().profile().downloadRequested.connect(download_requested)
            global download_directory
            download_directory = getSettingStr('downloadDirectory')
            while len(download_directory) > 0:
                if download_directory[-1] in ('/','\\'):
                    download_directory = download_directory[:-1]
                else:
                    break
            global download_dialog_size_x,download_dialog_size_y
            download_dialog_size_x,download_dialog_size_y = getSettingSize('fileDownloadDialogSize')

        if getSettingBool('enablePlugins'):
            QWebEngineSettings.globalSettings().setAttribute(QWebEngineSettings.PluginsEnabled,True)

        global home_page_url
        home_page_url = getSettingStr('homePage')
        

        navigate_home(self)

def load_finished(self):
    index = tabs.indexOf(self)
    title = str(self.browser.page().title())
    if len(title) > 20: title = title[:17]+'...'
    tabs.setTabText(index, title)

def navigate_home(self):
    self.browser.setUrl(QUrl(home_page_url))

def navigate_to_url(self):
    q = QUrl(self.urlbar.text())
    if q.scheme() == '':
        q.setScheme('http')
    self.browser.setUrl(q)

def update_urlbar(self,q):
    #if q.scheme() == 'https':
    #    self.httpsicon.setPixmap(QPixmap('ico/sec.jpg'))
    #else:
    #    self.httpsicon.setPixmap(QPixmap('ico/nosec.jpg'))
    
    self.urlbar.setText(q.toString())
    self.urlbar.setCursorPosition(0)

def download_requested(item):#QWebEngineDownloadItem
        name = os.path.basename(item.path())
        item.setPath('%s/%s'%(download_directory,name))
        #text,ok = QInputDialog.getText(self,'File download','Enter directory to download:',QLineEdit.Normal,item.path())
        inp = QInputDialog(None)
        inp.setInputMode(QInputDialog.TextInput)
        inp.setWindowTitle('File download')
        inp.setLabelText('Enter directory to download:')
        inp.setTextValue(item.path())
        inp.resize(download_dialog_size_x,download_dialog_size_y)
        if inp.exec_():
            text = inp.textValue()
            if not os.path.isdir(os.path.dirname(text)):
                ans = QMessageBox.question(None,'Directory does not exist','The selected directory does not exist, do you want it to be created?',QMessageBox.Yes,QMessageBox.No)
                if ans == QMessageBox.No:
                    return download_requested(item)
            if os.path.isfile(text):
                ans = QMessageBox.question(None,'File alredy exists','The selected file already exist, do you want to overwrite it?',QMessageBox.Yes,QMessageBox.No)
                if ans == QMessageBox.No:
                    return download_requested(item)
            item.setPath(text)
            item.accept()
  

def create_new_tab():
    window = MainWindow()
    tabs.addTab(window,'Loading...')
    return window

def remove_tab(index):
    widget = tabs.widget(index)
    if widget is not None:
        widget.deleteLater()
    tabs.removeTab(index)
    if len(tabs) == 0:
        QCoreApplication.quit()


home_page_url = None
download_directory = None
download_dialog_size_x = None
download_dialog_size_y = None


app = QApplication(sys.argv)
app.setApplicationName('Mnogo dobre mnogo mi haresva')
app.setOrganizationName('Troshiq Corp')
app.setOrganizationDomain('cakcakcak.cak')

tabs = QTabWidget()
tabs.setTabsClosable(True)
if getSettingBool('tabsMovable'):tabs.setMovable(True)
tabs.tabCloseRequested.connect(remove_tab)
tabs.setWindowTitle('Chestit rojden den na naiko zmeq')
tabs.setWindowIcon(QIcon('ico/ic.jpg'))

create_new_tab()





tabs.show()

app.exec_()

exit()

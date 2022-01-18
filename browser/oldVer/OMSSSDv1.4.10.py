
#v1.4.10


from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
#from PyQt5.QtWebKitWidgets import *
from PyQt5.QtWebEngineWidgets import *

import sys
import os
import time



def rais(text):
    try:
        app
    except:
        from subprocess import call
        call('start echo OMSSD Browser error: %s'%(text),shell=True)
    else:
        msg = QMessageBox()
        msg.setText('Error: %s'%(text))
        msg.exec_()
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
def getSettingSize(dimention,setName):
    data = getSettingRaw(setName)
    if data.count(',') != dimention-1:
        raisSetting(setName,'there should be %s "," not %s'%(dimention-1,data.count(',')))
    data = data.split(',')
    for x in range(len(data)):
        try: data[x] = int(data[x])
        except ValueError:
            x = x%10
            if x==0:vn='st'
            elif x==1:vn='nd'
            elif x==2:vn='rd'
            else:vn='th'
            raisSetting('the %s%s value should be an integer, not "%s"'%(x+1,vn,data[x]))
    return data
def getSettingInt(setname):
    return getSettingSize(1,setname)[0]

class Browser(QWebEngineView):
    def createWindow(self,mode):
        window = create_new_tab()
        return window.browser

class MainWindow(QMainWindow):
    def __init__(self,*args,**kwargs):
        super(MainWindow,self).__init__(*args,**kwargs)

        self.browser = Browser()

        self.setCentralWidget(self.browser)

        navtb = QToolBar('Uncheckni ako iskash da ostanesh bes toolbar')
        navtb.setMovable(getSettingBool('navtbMovable'))
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

        if getSettingBool('enableStopBtn'): 
            stop_btn = QAction('Stop',self)
            stop_btn.setStatusTip('Stop loading current page')
            stop_btn.triggered.connect(self.browser.stop)
            navtb.addAction(stop_btn)

        if getSettingBool('enableHomeBtn'):
            home_btn = QAction('Home',self)
            home_btn.setStatusTip('Home')
            home_btn.triggered.connect(lambda:navigate_home(self))
            navtb.addAction(home_btn)
            
        if getSettingBool('enableUrlBar'):
            self.urlbar = QLineEdit()
            self.urlbar.returnPressed.connect(lambda:navigate_to_url(self))
            navtb.addWidget(self.urlbar)
            self.browser.urlChanged.connect(lambda q:update_urlbar(self,q))

        add_tab_btn = QAction('New tab',self)
        add_tab_btn.triggered.connect(create_new_tab)
        navtb.addAction(add_tab_btn)

        #self.browser.loadStarted.connect(lambda:browser_load_started(self))
        self.browser.loadFinished.connect(lambda:browser_load_finished(self))

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
            download_dialog_size_x,download_dialog_size_y = getSettingSize(2,'fileDownloadDialogSize')




'''
def browser_load_started(self):
    index = tabs.indexOf(self)
    tabs.setTabText(index,'Loading page...')
'''

def browser_load_finished(self):
    index = tabs.indexOf(self)
    title = str(self.browser.page().title())
    if len(title) > tab_max_characters:
        title = title[:tab_max_characters-3]+'...'
    tabs.setTabText(index, title)

def navigate_home(self):
    self.browser.setUrl(QUrl(home_page_url))

def navigate_to_url(self):
    q = QUrl(self.urlbar.text())
    if q.scheme() == '':
        q.setScheme('http')
    self.browser.setUrl(q)

def update_urlbar(self,q):
    self.urlbar.setText(q.toString())
    self.urlbar.setCursorPosition(0)

def download_requested(item):#QWebEngineDownloadItem
    name = os.path.basename(item.path())
    item.setPath('%s/%s'%(download_directory,name))
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
    tabs.addTab(window,'New Tab')
    return window

def remove_tab(index):
    widget = tabs.widget(index)
    widget.close()
    widget.deleteLater()
    #if widget is not None:
    #    widget.deleteLater()
    tabs.removeTab(index)
    if len(tabs) == 0:
        QCoreApplication.quit()


home_page_url = None
download_directory = None
download_dialog_size_x = None
download_dialog_size_y = None
tab_max_characters = None

args = sys.argv
if getSettingBool('enableInternalFlashPlayer'):
    args += ['--ppapi-flash-path=/flashPlayer/pepflashplayer64_28_0_0_161.dll']
args += ['--ppapi-flash-version=%s'%(getSettingStr('flashPlayerVersionToUse'))]

app = QApplication(args);del args
app.setApplicationName('Mnogo dobre mnogo mi haresva')
app.setOrganizationName('Troshiq Corp')
app.setOrganizationDomain('cakcakcak.cak')

home_page_url = getSettingStr('homePage')
tab_max_characters = getSettingInt('tabMaxCharacters')

QWebEngineSettings.globalSettings().setAttribute(QWebEngineSettings.PluginsEnabled,getSettingBool('enablePlugins'))
QWebEngineSettings.globalSettings().setAttribute(QWebEngineSettings.JavascriptCanOpenWindows,getSettingBool('javascriptCanOpenWindows'))
QWebEngineSettings.globalSettings().setAttribute(QWebEngineSettings.JavascriptEnabled,getSettingBool('JavascriptEnabled'))
QWebEngineSettings.globalSettings().setAttribute(QWebEngineSettings.ScrollAnimatorEnabled,getSettingBool('ScrollAnimatorEnabled'))

tabs = QTabWidget()
tabs.setTabsClosable(True)
x,y = getSettingSize(2,'tabSize');tabs.setStyleSheet('QTabBar::tab { height: %spx; width: %spx}'%(y,x));del x,y
if getSettingBool('tabsMovable'):tabs.setMovable(True)
x,y,dx,dy = getSettingSize(4,'windowGeometry');tabs.setGeometry(x,y,dx,dy);del x,y,dx,dy
if getSettingBool('startBrowserMaximized'):tabs.setWindowState(Qt.WindowMaximized)
tabs.tabCloseRequested.connect(remove_tab)
tabs.setWindowTitle('Chestit rojden den na neiko zmeq')
if getSettingBool('enableIconInTopLeft'):tabs.setWindowIcon(QIcon('ico/ic.jpg'))

create_new_tab()
navigate_home(tabs.widget(0))

tabs.show()

sys.exit(app.exec_())

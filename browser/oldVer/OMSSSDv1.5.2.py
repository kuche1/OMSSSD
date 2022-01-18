
#1.5.2

#from PyQt5.QtCore import *
from PyQt5.QtCore import Qt,QUrl

#from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QMainWindow,QApplication,QToolBar,QAction,QLineEdit,QTabWidget,QMessageBox

#from PyQt5.QtGui import *
from PyQt5.QtGui import QIcon

#from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEngineView,QWebEngineSettings


import sys
import os

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

def getIco(iconame):
    return QIcon('ico/%s'%(iconame))

class Browser(QWebEngineView):
    def createWindow(self,mode):
        return mainwindow.add_new_tab()

class MainWindow(QMainWindow):
    def __init__(self,*args,**kwargs):
        super(MainWindow,self).__init__(*args,**kwargs)

        self.home_page_url = getSettingStr('homePage')
        self.tab_max_characters = getSettingInt('tabMaxCharacters')

        if getSettingBool('enableDownloads'):
            self.download_directory = getSettingStr('downloadDirectory')
            while len(self.download_directory) > 0:
                    if self.download_directory[-1] in ('/','\\'):
                        self.download_directory = self.download_directory[:-1]
                    else:
                        break

            self.download_dialog_size_x,self.download_dialog_size_y = getSettingSize(2,'fileDownloadDialogSize')
        else:
            #self.download_requested = lambda item:item.ignore()
            self.download_requested = lambda item:pass

        if getSettingBool('enableToolbarIcons')==False:
            global getIco
            getIco = lambda a:None

        navtb = QToolBar('Uncheckni ako iskash da ostanesh bes toolbar')
        navtb.setMovable(getSettingBool('navtbMovable'))
        self.addToolBar(navtb)

        if getSettingBool('enableBackBtn'):
            back_btn = QAction(getIco('zad.jpg'),'Back',self)
            back_btn.setStatusTip('Back to the previous page')
            back_btn.triggered.connect(self.back_btn_pressed)
            navtb.addAction(back_btn)

        if getSettingBool('enableForwardBtn'):
            next_btn = QAction(getIco('pred.jpg'),'Forward',self)
            next_btn.setStatusTip('Forward to next page')
            #next_btn.setShortcut('mouse4') ne raboti bash
            next_btn.triggered.connect(self.next_btn_pressed)
            navtb.addAction(next_btn)

        if getSettingBool('enableReloadBtn'):
            reload_btn = QAction(getIco('rel.jpg'),'Rload',self)
            reload_btn.setStatusTip('Reload')
            reload_btn.triggered.connect(self.reload_btn_pressed)
            navtb.addAction(reload_btn)

        if getSettingBool('enableStopBtn'): 
            stop_btn = QAction(getIco('can.jpg'),'Stop',self)
            stop_btn.setStatusTip('Stop loading current page')
            stop_btn.triggered.connect(self.stop_btn_pressed)
            navtb.addAction(stop_btn)

        if getSettingBool('enableHomeBtn'):
            home_btn = QAction(getIco('hom.jpg'),'Home',self)
            home_btn.setStatusTip('Home')
            home_btn.triggered.connect(self.home_btn_pressed)
            navtb.addAction(home_btn)
            
        if getSettingBool('enableUrlBar'):
            self.urlbar = QLineEdit()
            self.urlbar.returnPressed.connect(self.url_bar_return_pressed)
            navtb.addWidget(self.urlbar)

        add_tab_btn = QAction(getIco('nt.jpg'),'New tab',self)
        add_tab_btn.triggered.connect(self.add_new_tab_btn_pressed)
        navtb.addAction(add_tab_btn)
        

        self.tabs = QTabWidget(self)
        self.tabs.setTabsClosable(True)
        if getSettingBool('tabsMovable'):
            self.tabs.setMovable(True)
        if getSettingBool('startBrowserMaximized'):
            self.tabs.setWindowState(Qt.WindowMaximized)
        x,y = getSettingSize(2,'tabSize')
        self.tabs.setStyleSheet('QTabBar::tab { height: %spx; width: %spx}'%(y,x))
        x,y,dx,dy = getSettingSize(4,'windowGeometry')
        self.tabs.setGeometry(x,y,dx,dy)
        
        self.tabs.tabCloseRequested.connect(self.remove_tab)
        self.tabs.currentChanged.connect(self.tab_changed)
        self.setCentralWidget(self.tabs)


        QWebEngineSettings.globalSettings().setAttribute(QWebEngineSettings.PluginsEnabled,getSettingBool('enablePlugins'))
        QWebEngineSettings.globalSettings().setAttribute(QWebEngineSettings.JavascriptCanOpenWindows,getSettingBool('javascriptCanOpenWindows'))
        QWebEngineSettings.globalSettings().setAttribute(QWebEngineSettings.JavascriptEnabled,getSettingBool('JavascriptEnabled'))
        QWebEngineSettings.globalSettings().setAttribute(QWebEngineSettings.ScrollAnimatorEnabled,getSettingBool('ScrollAnimatorEnabled'))

        self.setWindowTitle('Chestit rojden den na neiko zmeq')
        if getSettingBool('enableIconInTopLeft'):
            self.setWindowIcon(QIcon('ico/ic.jpg'))


        self.add_new_tab_btn_pressed()

    def remove_tab(self,ind):
        tab = self.tabs.widget(ind)
        tab.close()
        tab.deleteLater()
        self.tabs.removeTab(ind)
        if len(self.tabs) == 0:
            QCoreApplicatiob.quit()
        
    def add_new_tab_btn_pressed(self):
        window = self.add_new_tab()
        self.go_url(window,self.home_page_url)

    def cur_go_url(self,url):
        self.go_url(self.get_cur_tab(),url)

    def go_url(self,brow,url):
        brow.setUrl(QUrl(url))

    def download_requested(self,item):
        name = os.path.basename(item.path())
        item.setPath('%s/%s'%(self.download_directory,name))
        inp = QInputDialog(self)
        inp.setInputMode(QInputDialog.TextInput)
        inp.setWindowTitle('File download')
        inp.setLabelText('Enter directory to download:')
        inp.setTextValue(item.path())
        inp.resize(self.download_dialog_size_x,self.download_dialog_size_y)
        if inp.exec_():
            text = inp.textValue()
            if not os.path.isdir(os.path.dirname(text)):
                ans = QMessageBox.question(self,'Directory does not exist','The selected directory does not exist, do you want it to be created?',QMessageBox.Yes,QMessageBox.No)
                if ans == QMessageBox.No:
                    return self.download_requested(item)
            if os.path.isfile(text):
                ans = QMessageBox.question(self,'File alredy exists','The selected file already exist, do you want to overwrite it?',QMessageBox.Yes,QMessageBox.No)
                if ans == QMessageBox.No:
                    return self.download_requested(item)
            item.setPath(text)
            item.accept()
        #else:
        #    item.ignore()

    def change_url_text(self,newtext):
        self.urlbar.setText(newtext)
        self.urlbar.setCursorPosition(0)

    def tab_changed(self,ind):
        tab = self.tabs.widget(ind)
        url = tab.url().toString()
        self.change_url_text(url)

    def get_cur_tab(self):
        return self.tabs.widget(self.tabs.currentIndex())

    def browser_load_finished(self,brow):
        ind = self.tabs.indexOf(brow)
        title = brow.page().title()
        if len(title) > self.tab_max_characters:
            title = title[:self.tab_max_characters-3]+'...'
        self.tabs.setTabText(ind,title)

    def url_bar_changed(self,q,brow):
        if brow == self.get_cur_tab():
            self.change_url_text(q.toString())

    def url_bar_return_pressed(self):
        q = QUrl(self.urlbar.text())
        if q.scheme() == '':
            q.setScheme('https')
        self.cur_go_url(q.toString())

    def home_btn_pressed(self):
        self.cur_go_url(self.home_page_url)

    def stop_btn_pressed(self):
        self.get_cur_tab().stop()

    def reload_btn_pressed(self):
        self.get_cur_tab().reload()

    def next_btn_pressed(self):
        self.get_cur_tab().forward()

    def back_btn_pressed(self):
        self.get_cur_tab().back()

    def add_new_tab(self):
        view = Browser()
        view.urlChanged.connect(lambda q:self.url_bar_changed(q,view))
        view.loadFinished.connect(lambda:self.browser_load_finished(view))

        view.page().profile().downloadRequested.connect(self.download_requested)
        
        self.tabs.addTab(view,'loading...')
        #self.tabs.setCurrentIndex(self.tabs.addTab(view,'loading...'))
        return view

args = sys.argv
if getSettingBool('enableInternalFlashPlayer'):
    args += ['--ppapi-flash-path=/flashPlayer/pepflashplayer64_28_0_0_161.dll']
args += ['--ppapi-flash-version=%s'%(getSettingStr('flashPlayerVersionToUse'))]

app = QApplication(args);del args
app.setApplicationName('Mnogo dobre mnogo mi haresva')
app.setOrganizationName('Troshiq Corp')
app.setOrganizationDomain('cakcakcak.cak')
mainwindow = MainWindow()
mainwindow.show()
sys.exit(app.exec_())

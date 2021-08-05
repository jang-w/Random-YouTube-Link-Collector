from selenium.webdriver.firefox.options import Options
from selenium import webdriver
import selenium
import random
import sys
import threading
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
import time

class RunRYL(QRunnable):
    def run(self):
        mainWindow.getVideos()

class SignalsRYL(QObject):
    linkSignal = Signal(object)
    statusSignal = Signal(object)

class window(QWidget):
    def __init__(self):
        super().__init__()
        with open('words.txt', 'r', encoding='utf-8') as w:
            self.words = w.readlines()

        browserThread = threading.Thread(target=self.setupBrowser)
        browserThread.start()

        self.threadpool = QThreadPool()
        
        self.showTitles = QRadioButton('Show Titles')
        self.showTitles.setChecked(True)
        self.showTitles.clicked.connect(self.changeDisplay)
        self.showLinks = QRadioButton('Show Links')
        self.showLinks.clicked.connect(self.changeDisplay)
        self.showWords = QRadioButton('Show Words')
        self.showWords.clicked.connect(self.changeDisplay)
        displayL = QVBoxLayout()
        displayL.addWidget(self.showTitles)
        displayL.addWidget(self.showLinks)
        displayL.addWidget(self.showWords)
        displayG = QGroupBox('Display')
        displayG.setLayout(displayL)

        self.addWord = QLineEdit()
        self.addWord.setPlaceholderText('Add word(s) to search')
        self.prepend = QRadioButton('Prepend')
        self.prepend.setChecked(True)
        self.append = QRadioButton('Append')
        bonusL = QVBoxLayout()
        bonusL.addWidget(self.addWord)
        bonusL.addWidget(self.prepend)
        bonusL.addWidget(self.append)
        self.bonusG = QGroupBox('Bonus Word')
        self.bonusG.setCheckable(True)
        self.bonusG.setLayout(bonusL)

        self.linkList = QTextBrowser()
        self.linkList.setOpenExternalLinks(True)
        self.linkList.setLineWrapMode(QTextEdit.NoWrap)
        self.signals = SignalsRYL()
        self.signals.linkSignal.connect(lambda s: self.linkList.append(s))
        self.signals.statusSignal.connect(lambda s: self.status.setText(s))

        self.numVideos = QSpinBox()
        start = QPushButton('Run')
        start.clicked.connect(self.startRYL)
        start.clicked.connect(lambda: self.linkList.clear())
        self.status = QLabel()
        startL = QVBoxLayout()
        startL.addWidget(self.numVideos)
        startL.addWidget(start)
        startL.addWidget(self.status)

        topL = QHBoxLayout()
        topL.addWidget(self.bonusG)
        topL.addWidget(displayG)
        topL.addLayout(startL)

        mainL = QGridLayout()
        mainL.addLayout(topL, 0, 0)
        mainL.addWidget(self.linkList, 1, 0)

        self.setLayout(mainL)
        self.show()

    def setupBrowser(self):
        fire_options = Options()
        fire_options.add_argument('--headless')
        fp = webdriver.FirefoxProfile()
        fp.set_preference('media.volume_scale', '0.0')
        self.videoBrowser = webdriver.Firefox(options=fire_options, firefox_profile=fp)

    def getVideos(self):
        self.signals.statusSignal.emit('Starting up...')

        while True:
            try:
                self.videoBrowser
            except AttributeError:
                continue
            break

        self.signals.statusSignal.emit('Collecting...')

        x = 0
        while x < self.numVideos.value():
            self.wordRoll = random.choice(self.words).strip()

            try:
                self.videoBrowser.get(self.printUrl())
                video = self.videoBrowser.find_elements_by_id('video-title')
                r = random.choice(range(1, len(video) - 1))
                self.videoTitle = video[r].text
                video[r].click()            
                x += 1 
            except IndexError:
                continue
            except selenium.common.exceptions.ElementNotInteractableException:
                continue
            except selenium.common.exceptions.NoSuchElementException:
                continue

            self.signals.linkSignal.emit(f'{x}: {self.printLink(x)}')

        self.signals.statusSignal.emit('Finished!')

    def closeEvent(self, event):
        self.videoBrowser.close()

    def startRYL(self):
        self.ryl = RunRYL()
        self.threadpool.globalInstance().start(self.ryl)
        self.linkDisplays = {}

    def printUrl(self):
        if not self.bonusG.isChecked():
            urlGet = f'https://youtube.com/results?search_query={self.wordRoll}+before%3A2012-08-08'
        else:
            if self.prepend.isChecked():
                urlGet = f'https://youtube.com/results?search_query={self.addWord.text()}+{self.wordRoll}+before%3A2012-08-08'
            elif self.append.isChecked():
                urlGet = f'https://youtube.com/results?search_query={self.wordRoll}+{self.addWord.text()}+before%3A2012-08-08'
        return urlGet
    
    def printLink(self, count):
        linkTitle = f'<a href="{self.videoBrowser.current_url}">{self.videoTitle}</a>'
        linkLink = f'<a href="{self.videoBrowser.current_url}">{self.videoBrowser.current_url}</a>'
        linkWord = f'<a href="{self.videoBrowser.current_url}">{self.wordRoll}</a>'

        singleLink = [linkTitle, linkLink, linkWord]

        self.linkDisplays[count] = singleLink
        
        if self.showTitles.isChecked():
            return linkTitle
        elif self.showLinks.isChecked():
            return linkLink
        elif self.showWords.isChecked():
            return linkWord
    
    def changeDisplay(self):
        self.linkList.clear()
        if self.showTitles.isChecked():
            for x in self.linkDisplays:
                self.linkList.append(f'{x}: {self.linkDisplays[x][0]}')
        elif self.showLinks.isChecked():
            for x in self.linkDisplays:
                self.linkList.append(f'{x}: {self.linkDisplays[x][1]}')
        elif self.showWords.isChecked():
            for x in self.linkDisplays:
                self.linkList.append(f'{x}: {self.linkDisplays[x][2]}')

if __name__ == '__main__':
    app = QApplication([])
    mainWindow = window()
    sys.exit(app.exec_())
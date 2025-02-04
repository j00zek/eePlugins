# -*- coding: utf-8 -*-
# @j00zek 2014/2015/2016/2017/2019
#
# changes/improvements:
# - translation of cmd texts with common structure _(), e.g. echo "_(this is an example)"
# - safe for tuners with small memory size
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3

from enigma import eConsoleAppContainer, eServiceReference, getDesktop, eTimer
from Screens.InfoBar import InfoBar
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.ScrollLabel import ScrollLabel

import os
#
from Screens.Screen import Screen

from emukodi.xbmcE2 import *

def ensure_str(string2decode):
    if isinstance(string2decode, bytes):
        return string2decode.decode('utf-8', 'ignore')
    else:
        return string2decode

class emukodiConsole(Screen):
    if getDesktop(0).size().width() >= 1920:
        skin = """
          <screen name="emukodiConsole" position="center,center" size="800,400" title="emukodi execution...">
            <widget name="text" position="0,0" size="800,400" font="Console;28" backgroundColor="background" transparent="1"/>
          </screen>"""
    else:
        skin = """
          <screen position="center,center" size="600,400" title="emukodi execution..." >
            <widget name="text" position="0,0" size="600,400" font="Console;18" />
          </screen>"""
        
    def __init__(self, session, title = "emukodiConsole", cmdlist = None, finishedCallback = None, closeOnSuccess = False, endText = "\nKoniec :D"):
        Screen.__init__(self, session)
        self.finishedCallback = finishedCallback
        self.closeOnSuccess = closeOnSuccess
        self.errorOcurred = False

        self["text"] = ScrollLabel("")
        self["actions"] = ActionMap(["WizardActions", "DirectionActions"], 
        {
            "ok": self.cancel,
            "back": self.cancel,
            "up": self["text"].pageUp,
            "down": self["text"].pageDown
        }, -1)
        
        self.cmdlist = cmdlist
        self.newtitle = title
        self.endText = endText
        
        self.onShown.append(self.updateTitle)
        
        self.container = eConsoleAppContainer()
        self.run = 0
        self.container.appClosed.append(self.runFinished)
        self.container.dataAvail.append(self.dataAvail)
        self.refreshTimer = eTimer()
        self.refreshTimer.callback.append(self.TimedRefresh)
        self.onLayoutFinish.append(self.startRun) # dont start before gui is finished
        
    def updateTitle(self):
        self.setTitle(self.newtitle)

    def doExec(self, cmd):
        if isinstance(cmd, (list, tuple)):
            return self.container.execute(cmd[0], *cmd)
        else:
            return self.container.execute(cmd)

    def startRun(self):
        self.refreshTimer.start(1000, False) #False = continously
        self["text"].setText("" + "\n\n")
        with open("/proc/sys/vm/drop_caches", "w") as f: f.write("1\n")
        log(self.cmdlist[self.run])
        if self.doExec(self.cmdlist[self.run]):  # Start of container application failed so we must call runFinished manually.
            self.runFinished(-1) # so we must call runFinished manual

    def runFinished(self, retval):
        if retval:
            self.errorOcurred = True
        self.run += 1
        if self.run != len(self.cmdlist):
            with open("/proc/sys/vm/drop_caches", "w") as f: f.write("1\n")
            log(self.cmdlist[self.run])
            if self.doExec(self.cmdlist[self.run]):  # Start of container application failed so we must call runFinished manually.
                self.runFinished(-1) # so we must call runFinished manual
        else:
            #lastpage = self["text"].isAtLastPage()
            myText = self["text"].getText()
            if not self.errorOcurred:
                myText += self.endText;
            else:
                myText += '\nWystąpił Błąd, jeśli potrzebujesz pomocy załącz log systemowy w wątku na forum !!!';
            self["text"].setText(myText)
            #if lastpage:
            self["text"].lastPage()
            print('[SLK]>[emukodiConsole.runFinished(errorOcurred=%s)] displayed text:\n %s' % (self.errorOcurred, myText) )
            if self.finishedCallback is not None:
                self.finishedCallback()
            if not self.errorOcurred and self.closeOnSuccess:
                self.cancel()

    def backButton(self):
        self.cancel(True)

    def cancel(self, force=False):
        if force or self.run == len(self.cmdlist):
            self.close()
            self.container.appClosed.remove(self.runFinished)
            self.container.dataAvail.remove(self.dataAvail)
            self.refreshTimer.stop()
            self.refreshTimer.callback.remove(self.TimedRefresh)
            if self.run != len(self.cmdlist):
                self.container.kill()

    def dataAvail(self, myText):
        myText =  ensure_str(myText)
        myText = myText.replace('Dialog().Notification:','').replace(", 'info', None",'')
        #lastpage = self["text"].isAtLastPage()
        tmpText = self["text"].getText()
        #printDBG('>>>>> linii w buforze: %s\n' % tmpText.count('\n'))
        if tmpText.count('\n') > 200: # za dlugie teksty powoduja ze wszystko ginie, jakby bufor sie przepelnia
            tmpText = "...\n" + "\n".join(tmpText.split("\n")[20:])
        self["text"].setText( tmpText + myText)
        #if lastpage:
        self["text"].lastPage()

    def TimedRefresh(self):
        tmpFile = os.path.join(working_dir,'xbmcgui_DialogProgress')
        if os.path.exists(tmpFile):
            DialogText = open(tmpFile, "r").read().strip()
            self["text"].setText(DialogText)
            return

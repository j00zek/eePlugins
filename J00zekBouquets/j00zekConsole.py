# -*- coding: utf-8 -*-
# @j00zek 2014/2015/2016/2017/2019
#
# changes/improvements:
# - translation of cmd texts with common structure _(), e.g. echo "_(this is an example)"
# - safe for tuners with small memory size
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3

from enigma import eConsoleAppContainer, eServiceReference, getDesktop
from Screens.InfoBar import InfoBar
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.ScrollLabel import ScrollLabel
from Plugins.Extensions.J00zekBouquets.inits import *
#
#from Components.Pixmap import Pixmap
#from enigma import eTimer
#from os import system as os_system, popen as os_popen
#from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
#from Screens.MessageBox import MessageBox
#from Screens.ChoiceBox import ChoiceBox

class j00zekConsole(Screen):
    if getDesktop(0).size().width() >= 1920:
        skin = """
          <screen name="j00zekConsole" position="60,560" size="600,400" title="Command execution...">
            <widget name="text" position="0,0" size="600,400" font="Console;18" backgroundColor="background" transparent="1"/>
          </screen>"""
    else:
        skin = """
          <screen position="40,300" size="550,400" title="Command execution..." >
            <widget name="text" position="0,0" size="550,400" font="Console;14" />
          </screen>"""
        
    def __init__(self, session, title = "j00zekBouquetsConsole", cmdlist = None, finishedCallback = None, closeOnSuccess = False, endText = "\nUżyj strzałek góra/dół do przewinięcia tekstu. OK zamyka okno"):
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
        self.onLayoutFinish.append(self.startRun) # dont start before gui is finished

    def updateTitle(self):
        self.setTitle(self.newtitle)

    def startRun(self):
        self["text"].setText("" + "\n\n")
        #print "TranslatedConsole: executing in run", self.run, " the command:", self.cmdlist[self.run]
        with open("/proc/sys/vm/drop_caches", "w") as f: f.write("1\n")
        if self.container.execute(self.cmdlist[self.run]): #start of container application failed...
            self.runFinished(-1) # so we must call runFinished manual

    def runFinished(self, retval):
        if retval:
            self.errorOcurred = True
        self.run += 1
        if self.run != len(self.cmdlist):
            with open("/proc/sys/vm/drop_caches", "w") as f: f.write("1\n")
            if self.container.execute(self.cmdlist[self.run]): #start of container application failed...
                self.runFinished(-1) # so we must call runFinished manual
        else:
            #lastpage = self["text"].isAtLastPage()
            myText = self["text"].getText()
            myText += self.endText;
            self["text"].setText(myText)
            #if lastpage:
            self["text"].lastPage()
            if self.finishedCallback is not None:
                self.finishedCallback()
            if not self.errorOcurred and self.closeOnSuccess:
                self.cancel()

    def cancel(self):
        if self.run == len(self.cmdlist):
            self.close()
            self.container.appClosed.remove(self.runFinished)
            self.container.dataAvail.remove(self.dataAvail)

    def dataAvail(self, myText):
        myText =  str(myText)
        try: myText.decode('utf-8')
        except: pass
        #lastpage = self["text"].isAtLastPage()
        #with open("/tmp/JB", "a") as f: f.write(myText)
        if myText.find("zapTo(") > -1:
            dvbService = myText.split('zapTo(', 1)[1]
            if dvbService.find(")") > -1:
                dvbService = dvbService.split(')', 1)[0]
                serviceDVB = eServiceReference(dvbService)
                InfoBar.instance.servicelist.clearPath()
                InfoBar.instance.servicelist.enterPath(serviceDVB)
                InfoBar.instance.servicelist.setCurrentSelection(serviceDVB)
                InfoBar.instance.servicelist.zap()
                myText = myText.replace("zapTo(%s)" % dvbService ,"Przełączanie na kanał nadający dane o numeracji...")
            #with open("/tmp/JB", "a") as f: f.write("aaaa" + dvbService)
        tmpText = self["text"].getText()
        if tmpText.count('\n') > 200: # za dlugie texty powoduja ze wszystko ginie, jakby bufor sie przepelnial
            tmpText = "...\n" + "\n".join(tmpText.split("\n")[20:])
        self["text"].setText( tmpText + myText)
        #if lastpage:
        self["text"].lastPage()

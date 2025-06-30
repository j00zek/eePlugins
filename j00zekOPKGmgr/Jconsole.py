# -*- coding: utf-8 -*-
# @j00zek 2014-2022
#
# changes/improvements:
# - translation of cmd texts with common structure _(), e.g. echo "_(this is an example)"
# - safe for tuners with small memory size
from __future__ import absolute_import #zmiana strategii ladowania modulow w py2 z relative na absolute jak w py3

from enigma import eConsoleAppContainer
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.ScrollLabel import ScrollLabel
from . import _
#
from Components.Pixmap import Pixmap
from enigma import ePicLoad, ePoint, getDesktop, eTimer, ePixmap
from os import system as os_system, popen as os_popen, path
#from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox

from sys import version_info

PyMajorVersion = version_info.major

def substring_2_translate(text):
    to_translate = text.split('_(', 2)
    text = to_translate[1]
    to_translate = text.split(')', 2)
    text = to_translate[0]
    return text
    
def __(txt):
    if PyMajorVersion == 3:
        txt = txt.decode('utf-8')
    if txt.find('_(') == -1:
        txt = _(txt)
    else:
        index = 0
        while txt.find('_(') != -1:
            tmptxt = substring_2_translate(txt)
            translated_tmptxt = _(tmptxt)
            txt = txt.replace('_(' + tmptxt + ')', translated_tmptxt)
            index += 1
            if index == 10:
                break
    for x in ['Downloading', 'Inflating' , 'Installing', 'Upgrading', 'Configuring']:
        txt = txt.replace(x, _(x))

    return txt

class Jconsole(Screen):
    #TODO move this to skin.xml
    skin = """
        <screen position="40,300" size="550,400" title="Command execution..." >
            <widget name="text" position="0,0" size="550,400" font="Console;14" />
        </screen>"""
        
    def __init__(self, session, title = "UserSkinconsole", cmdlist = None, finishedCallback = None, closeOnSuccess = False):
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
        print("TranslatedConsole: executing in run", self.run, " the command:", self.cmdlist[self.run])
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
            str = self["text"].getText()
            str += _("\nUse up/down arrows to scroll text. OK closes window");
            self["text"].setText(str)
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

    def dataAvail(self, str):
        #lastpage = self["text"].isAtLastPage()
        tmpText = self["text"].getText()
        if tmpText.count('\n') > 200: # za dlugie texty powoduja ze wszystko ginie, jakby bufor sie przepelnial
            tmpText = "...\n" + "\n".join(tmpText.split("\n")[20:])
        self["text"].setText( tmpText + __(str))
        #if lastpage:
        self["text"].lastPage()

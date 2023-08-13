#
# j00zek 2018-2022
#
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Components.Converter.Converter import Converter
from Components.Element import cached
from Components.j00zekComponents import isPY2 
from enigma import eConsoleAppContainer, eTimer

import sys
PyMajorVersion = sys.version_info.major

DBG = False
if DBG: 
    from Components.j00zekComponents import j00zekDEBUG
    checkDelay = 60000 #check once a minute for tests
else:
    checkDelay = 86400000 #check once a day 86400000 = 1000ms * 60 * 60 * 24
    
class j00zekOPKGupgradeCheck(Converter, object):
    def __init__(self, arg):
        Converter.__init__(self, arg)
        if DBG: j00zekDEBUG('[j00zekOPKGupgradeCheck:__init__] >>>')
        self.currState = False
        self.retstr = ''
        self.container = eConsoleAppContainer()
        self.container.appClosed.append(self.appClosed)
        self.container.dataAvail.append(self.dataAvail)
        self.checkTimer = eTimer()
        self.checkTimer.callback.append(self.checkOPKG)
        self.checkTimer.start(60000, True) #initial check after a minute from init

    @cached
    def getBoolean(self):
        if DBG: j00zekDEBUG('[j00zekOPKGupgradeCheck:getBoolean] self.currState=%s' % self.currState)
        return self.currState

    boolean = property(getBoolean)
    
    def checkOPKG(self):
        if DBG: j00zekDEBUG('[j00zekOPKGupgradeCheck:checkOPKG] >>>')
        self.checkTimer.stop()
        self.checkTimer.start(checkDelay)
        self.retstr = ''
        cmd=[]
        cmd.append('opkg update > /dev/null')
        cmd.append('opkg list-upgradable')
        self.container.execute(";".join(cmd))
    
    def appClosed(self, retval):
        if DBG: j00zekDEBUG("[j00zekOPKGupgradeCheck:appClosed] retval=%s" % str(retval))
        if self.retstr.find('j00zek') > 0:
            self.currState = True
        else:
            self.currState = False
        self.retstr = ''
        if DBG: j00zekDEBUG("[j00zekOPKGupgradeCheck:dataAvail] self.currState=%s" % self.currState)

    def dataAvail(self, conStr):
        if DBG: j00zekDEBUG("[j00zekOPKGupgradeCheck:dataAvail] %s" % conStr)
        if isPY2():
            self.retstr += str(conStr)
        else:
            self.retstr += str(conStr, 'utf-8', 'ignore')

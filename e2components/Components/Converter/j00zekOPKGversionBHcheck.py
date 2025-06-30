#
# j00zek 2018-2022
#
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Components.Converter.Converter import Converter
from Components.Converter.Poll import Poll
from Components.Element import cached
from Components.j00zekComponents import isPY2 
from enigma import eConsoleAppContainer

DBG = False
if DBG: from Components.j00zekComponents import j00zekDEBUG

BlackHarmonyVersion = '?'

class j00zekOPKGversionBHcheck(Poll, Converter, object):

    def __init__(self, arg):
        if DBG: j00zekDEBUG('[j00zekOPKGversionBHcheck:__init__] >>>')

        Converter.__init__(self, arg)
        Poll.__init__(self) 
        self.poll_interval = 1000
        
        if BlackHarmonyVersion == '?': self.poll_enabled = True
        else: self.poll_enabled = False
        
        self.retstr = ''
        if BlackHarmonyVersion == '?':
            self.container = eConsoleAppContainer()
            self.container.appClosed.append(self.appClosed)
            self.container.dataAvail.append(self.dataAvail)
            self.checkOPKG()

    @cached
    def getText(self):
        if DBG: j00zekDEBUG('[j00zekOPKGversionBHcheck:getText] BlackHarmonyVersion=%s' % BlackHarmonyVersion)
        return BlackHarmonyVersion

    text = property(getText) 
    
    def changed(self, what):
        if what[0] == self.CHANGED_POLL:
            if BlackHarmonyVersion != '?': self.poll_enabled = False
            self.downstream_elements.changed(what)
            
    def checkOPKG(self):
        if DBG: j00zekDEBUG('[j00zekOPKGversionBHcheck:checkOPKG] >>>')
        self.retstr = ''
        cmd=[]
        cmd.append('opkg update > /dev/null')
        cmd.append('opkg list-installed|grep enigma2-plugin-skins--j00zeks-blackharmonyfhd')
        self.container.execute(";".join(cmd))
    
    def appClosed(self, retval):
        if DBG: j00zekDEBUG("[j00zekOPKGversionBHcheck:appClosed] retval=%s, retstr='%s'" % (str(retval), self.retstr))
        if self.retstr.find('enigma2-plugin-skins--j00zeks-blackharmonyfhd') >= 0:
            global BlackHarmonyVersion
            BlackHarmonyVersion = self.retstr.replace('enigma2-plugin-skins--j00zeks-blackharmonyfhd','').split('-')[1].strip()
        self.retstr = ''
        if DBG: j00zekDEBUG("[j00zekOPKGversionBHcheck:appClosed] BlackHarmonyVersion='%s'" % BlackHarmonyVersion)

    def dataAvail(self, conStr):
        if DBG: j00zekDEBUG("[j00zekOPKGversionBHcheck:dataAvail] %s" % conStr)
        if isPY2():
            self.retstr += str(conStr)
        else:
            self.retstr += str(conStr, 'utf-8', 'ignore')

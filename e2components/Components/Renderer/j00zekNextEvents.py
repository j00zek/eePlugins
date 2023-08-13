from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Components.Renderer.Renderer import Renderer #ATV7.0,EGAMI10
from Components.config import config
from Components.VariableText import VariableText
from enigma import eLabel, eEPGCache
from time import time, localtime
from datetime import datetime

class j00zekNextEvents(VariableText, Renderer):
    def __init__(self):
        Renderer.__init__(self)
        VariableText.__init__(self)
        self.epgcache = eEPGCache.getInstance()

    GUI_WIDGET = eLabel

    def connect(self, source):
        Renderer.connect(self, source)
        self.changed((self.CHANGED_DEFAULT,))

    def changed(self, what):
        now = datetime.now()
        currentEPOC = int(time())
        if what[0] == self.CHANGED_CLEAR:
            self.text = ""
        else:
            list = self.epgcache.lookupEvent([ 'BDT', (self.source.text, 0, -1, 360) ])
            text = ""
            if len(list):
                i = 1
                j = 1
                for event in list:
                    if len(event) == 3:
                        begin = localtime(event[0])
                        end = localtime(event[0]+event[1])
                        try:
                            if currentEPOC < event[0]:
                                event_str = "%02d:%02d - %02d:%02d  %s\n" % (begin[3],begin[4],end[3],end[4], event[2])
                                text = text + event_str
                                i = i + 1
                        except:
                            pass
                    j += 1
                    if i>=6 or j>10:
                        break
            self.text = text

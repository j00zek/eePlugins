# j00zek: this file has changed name just to avoid errors using opkg (situation when file was installed by different pockage)
#
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Components.VariableText import VariableText
from enigma import eLabel, eEPGCache

from Components.Renderer.Renderer import Renderer #ATV7.0,EGAMI10

from time import localtime

class j00zekModEGEpgListNobile(Renderer, VariableText):

    def __init__(self):
        Renderer.__init__(self)
        VariableText.__init__(self)
        self.epgcache = eEPGCache.getInstance()

    GUI_WIDGET = eLabel

    def changed(self, what):
        event = self.source.event
        if event is None:
            self.text = ''
            return
        else:
            service = self.source.service
            text = ''
            evt = None
            if self.epgcache is not None:
                evt = self.epgcache.lookupEvent(['IBDCT', (service.toString(),
                  0,
                  -1,
                  -1)])
            if evt:
                maxx = 0
                for x in evt:
                    if maxx > 1:
                        if x[4]:
                            t = localtime(x[1])
                            text = text + '%02d:%02d %s\n' % (t[3], t[4], x[4])
                        else:
                            text = text + 'n/a\n'
                    maxx += 1
                    if maxx > 31:
                        break

            self.text = text
            return
            return